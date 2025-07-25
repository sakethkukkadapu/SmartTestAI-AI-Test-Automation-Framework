"""
Notification module for sending test results via Slack and email.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Union

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

class NotificationSender:
    """Sends test result notifications via Slack and email."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the notification sender with configuration.
        
        Args:
            config: Notification configuration dict from config file
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_slack_notification(self, summary: Dict[str, Any], 
                               detailed: bool = False) -> bool:
        """
        Send test results notification to Slack.
        
        Args:
            summary: Test result summary
            detailed: Whether to include detailed results
            
        Returns:
            True if notification was sent successfully
        """
        if not SLACK_AVAILABLE:
            self.logger.warning("slack_sdk not installed. Cannot send Slack notifications.")
            return False
            
        slack_config = self.config.get("slack", {})
        if not slack_config.get("enabled", False):
            self.logger.info("Slack notifications disabled in config.")
            return False
            
        webhook_url = slack_config.get("webhook_url")
        if not webhook_url:
            self.logger.error("Slack webhook URL not provided in config.")
            return False
            
        # Create client
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))
        channel = slack_config.get("channel", "#api-testing")
        
        # Create message blocks
        blocks = self._create_slack_message_blocks(summary, detailed)
        
        try:
            # Send message
            if webhook_url.startswith("https://hooks.slack.com"):
                # Using webhook
                from slack_sdk.webhook import WebhookClient
                webhook_client = WebhookClient(webhook_url)
                response = webhook_client.send(
                    text=f"Test Run Summary: {summary.get('title', 'SmartTestAI Results')}",
                    blocks=blocks
                )
                return response.status_code == 200
            else:
                # Using bot token
                response = client.chat_postMessage(
                    channel=channel,
                    text=f"Test Run Summary: {summary.get('title', 'SmartTestAI Results')}",
                    blocks=blocks
                )
                return True
                
        except SlackApiError as e:
            self.logger.error(f"Error sending Slack notification: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending Slack notification: {e}")
            return False
            
    def send_email_notification(self, summary: Dict[str, Any], 
                               detailed: bool = False) -> bool:
        """
        Send test results notification via email.
        
        Args:
            summary: Test result summary
            detailed: Whether to include detailed results
            
        Returns:
            True if notification was sent successfully
        """
        email_config = self.config.get("email", {})
        if not email_config.get("enabled", False):
            self.logger.info("Email notifications disabled in config.")
            return False
            
        smtp_server = email_config.get("smtp_server")
        port = email_config.get("port", 587)
        use_tls = email_config.get("use_tls", True)
        
        from_email = email_config.get("from_email")
        recipients = email_config.get("recipients", [])
        
        if not smtp_server or not from_email or not recipients:
            self.logger.error("Missing email configuration parameters.")
            return False
            
        # Create email message
        message = self._create_email_message(summary, detailed, from_email, recipients)
        
        try:
            # Send email
            with smtplib.SMTP(smtp_server, port) as server:
                if use_tls:
                    server.starttls()
                    
                if email_config.get("username") and email_config.get("password"):
                    server.login(email_config.get("username"), email_config.get("password"))
                    
                server.send_message(message)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
            return False
            
    def _create_slack_message_blocks(self, summary: Dict[str, Any], 
                                    detailed: bool) -> List[Dict[str, Any]]:
        """Create formatted Slack message blocks from test summary."""
        title = summary.get("title", "SmartTestAI Test Results")
        total = summary.get("total_tests", 0)
        passed = summary.get("passed_tests", 0)
        failed = summary.get("failed_tests", 0)
        duration = summary.get("duration_seconds", 0)
        
        # Calculate pass percentage
        pass_percentage = 0
        if total > 0:
            pass_percentage = (passed / total) * 100
            
        # Determine color based on results
        color = "#36a64f"  # green
        if failed > 0:
            if pass_percentage < 50:
                color = "#ff0000"  # red
            else:
                color = "#ff9900"  # orange
                
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tests:*\n{total}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{'✅ All Passed' if failed == 0 else '❌ Some Tests Failed'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n{passed} ({pass_percentage:.1f}%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n{failed}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Duration: {duration:.2f} seconds | Generated by SmartTestAI"
                    }
                ]
            }
        ]
        
        # Add failures if detailed and any tests failed
        if detailed and failed > 0:
            failures = summary.get("failures", [])
            if failures:
                blocks.append({
                    "type": "divider"
                })
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Failed Tests:*"
                    }
                })
                
                for i, failure in enumerate(failures[:5]):  # Limit to 5 failures
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{failure.get('name', f'Test {i+1}')}*\n{failure.get('message', 'No error message')}"
                        }
                    })
                    
                if len(failures) > 5:
                    blocks.append({
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"_...and {len(failures) - 5} more failures_"
                            }
                        ]
                    })
                
        return blocks
        
    def _create_email_message(self, summary: Dict[str, Any], detailed: bool,
                            from_email: str, recipients: List[str]) -> MIMEMultipart:
        """Create formatted email message from test summary."""
        message = MIMEMultipart("alternative")
        message["Subject"] = f"SmartTestAI Results: {summary.get('title', 'Test Results')}"
        message["From"] = from_email
        message["To"] = ", ".join(recipients)
        
        title = summary.get("title", "SmartTestAI Test Results")
        total = summary.get("total_tests", 0)
        passed = summary.get("passed_tests", 0)
        failed = summary.get("failed_tests", 0)
        duration = summary.get("duration_seconds", 0)
        
        # Calculate pass percentage
        pass_percentage = 0
        if total > 0:
            pass_percentage = (passed / total) * 100
            
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h1>{title}</h1>
            <table width="100%" cellpadding="5" cellspacing="0">
                <tr>
                    <td><strong>Total Tests:</strong></td>
                    <td>{total}</td>
                    <td><strong>Status:</strong></td>
                    <td>{'✅ All Passed' if failed == 0 else '❌ Some Tests Failed'}</td>
                </tr>
                <tr>
                    <td><strong>Passed:</strong></td>
                    <td>{passed} ({pass_percentage:.1f}%)</td>
                    <td><strong>Failed:</strong></td>
                    <td>{failed}</td>
                </tr>
            </table>
            <p>Duration: {duration:.2f} seconds</p>
        """
        
        # Add failures if detailed and any tests failed
        if detailed and failed > 0:
            failures = summary.get("failures", [])
            if failures:
                html_content += "<h2>Failed Tests:</h2><ul>"
                
                for failure in failures:
                    html_content += f"""
                    <li>
                        <strong>{failure.get('name', 'Unknown Test')}</strong><br/>
                        {failure.get('message', 'No error message')}
                    </li>
                    """
                    
                html_content += "</ul>"
                
        html_content += """
        <hr>
        <p><em>Generated by SmartTestAI - Automated Testing Framework</em></p>
        </body>
        </html>
        """
        
        # Create plain text version as fallback
        text_content = f"""
        {title}
        
        Total Tests: {total}
        Status: {'All Passed' if failed == 0 else 'Some Tests Failed'}
        Passed: {passed} ({pass_percentage:.1f}%)
        Failed: {failed}
        
        Duration: {duration:.2f} seconds
        """
        
        if detailed and failed > 0:
            failures = summary.get("failures", [])
            if failures:
                text_content += "\nFailed Tests:\n"
                
                for failure in failures:
                    text_content += f"- {failure.get('name', 'Unknown Test')}: {failure.get('message', 'No error message')}\n"
        
        text_content += "\nGenerated by SmartTestAI - Automated Testing Framework"
        
        # Attach both versions to the email
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))
        
        return message
