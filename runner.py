#!/usr/bin/env python3
"""
SmartTestAI Test Runner

CLI-based runner that loads test config, executes tests, and generates reports.
Integrates with notification systems to send results.
"""
import os
import sys
import time
import json
import argparse
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import concurrent.futures

from config.config_loader import ConfigLoader
from utils.report_generator import ReportGenerator
from utils.notifications import NotificationSender
from utils import setup_logger, get_timestamp, format_duration
from ai.prompt_generator import TestPromptGenerator

class TestRunner:
    """Main test runner for SmartTestAI framework."""
    
    def __init__(self, config_path: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the test runner.
        
        Args:
            config_path: Path to config file (optional)
            log_level: Logging level
        """
        # Setup logger
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"smarttestai_{get_timestamp()}.log")
        self.logger = setup_logger("smarttestai", log_file, getattr(sys, log_level.upper(), "INFO"))
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # Set up report generator
        report_config = self.config.get("reporting", {})
        self.report_generator = ReportGenerator(report_config.get("output_dir", "./reports"))
        
        # Set up notification sender
        notification_config = self.config.get("notifications", {})
        self.notification_sender = NotificationSender(notification_config)
        
        # Initialize results storage
        self.test_results = {
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0
            },
            "tests": []
        }
        
        self.base_url = self.config_loader.get_base_url()
        self.logger.info(f"Initialized SmartTestAI runner with config from {config_path}")
        self.logger.info(f"Base URL: {self.base_url}")
        
    def discover_tests(self, path: str = None, pattern: str = "test_*.py") -> List[str]:
        """
        Discover test files matching pattern.
        
        Args:
            path: Path to search for tests
            pattern: Test file pattern
            
        Returns:
            List of discovered test files
        """
        if not path:
            path = os.path.join(os.path.dirname(__file__), "tests")
            
        discovered_tests = []
        
        for root, _, files in os.walk(path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_path = os.path.join(root, file)
                    discovered_tests.append(test_path)
                    
        self.logger.info(f"Discovered {len(discovered_tests)} test files")
        return discovered_tests
    
    def run_test_file(self, test_file: str, test_args: List[str] = None) -> Dict[str, Any]:
        """
        Run a single test file using pytest.
        
        Args:
            test_file: Path to test file
            test_args: Additional pytest arguments
            
        Returns:
            Dictionary with test results
        """
        if test_args is None:
            test_args = []
            
        self.logger.info(f"Running test file: {test_file}")
        
        # Set up command
        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--json-report"]
        cmd.extend(test_args)
        
        # Run pytest
        start_time = time.time()
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        duration = time.time() - start_time
        
        # Parse results
        report_file = os.path.join(os.path.dirname(test_file), ".report.json")
        results = {
            "file": test_file,
            "duration": duration,
            "return_code": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "tests": []
        }
        
        # Try to parse JSON report if available
        try:
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                    results["report"] = report_data
                    
                    # Extract test results
                    for test_result in report_data.get("tests", []):
                        test_info = {
                            "name": test_result.get("nodeid", "").split("::")[-1],
                            "classname": test_result.get("nodeid", "").split("::")[-2] if "::" in test_result.get("nodeid", "") else "",
                            "status": "pass" if test_result.get("outcome") == "passed" else "fail" if test_result.get("outcome") == "failed" else "skip",
                            "duration": test_result.get("duration", 0),
                            "details": test_result.get("nodeid", "")
                        }
                        
                        if test_result.get("outcome") == "failed":
                            test_info["error"] = test_result.get("call", {}).get("longrepr", "")
                            test_info["error_type"] = test_result.get("call", {}).get("crash", {}).get("typename", "AssertionError")
                            
                        results["tests"].append(test_info)
        except Exception as e:
            self.logger.error(f"Error parsing test report: {e}")
            
        return results
    
    def run_tests(self, test_files: List[str] = None, parallel: bool = None, 
                 test_args: List[str] = None) -> Dict[str, Any]:
        """
        Run multiple test files.
        
        Args:
            test_files: List of test files to run
            parallel: Whether to run tests in parallel
            test_args: Additional pytest arguments
            
        Returns:
            Dictionary with all test results
        """
        if test_files is None:
            test_files = self.discover_tests()
            
        if parallel is None:
            parallel = self.config.get("execution", {}).get("parallel", False)
            
        if test_args is None:
            test_args = []
            
        max_workers = self.config.get("execution", {}).get("max_workers", 4) if parallel else 1
        
        start_time = time.time()
        all_results = []
        
        self.logger.info(f"Running {len(test_files)} test files {'in parallel' if parallel else 'sequentially'}")
        
        if parallel and len(test_files) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(self.run_test_file, file, test_args): file 
                    for file in test_files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        all_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error running tests in {file}: {e}")
        else:
            for file in test_files:
                try:
                    result = self.run_test_file(file, test_args)
                    all_results.append(result)
                except Exception as e:
                    self.logger.error(f"Error running tests in {file}: {e}")
        
        # Calculate summary
        duration = time.time() - start_time
        
        passed = 0
        failed = 0
        skipped = 0
        tests = []
        
        for result in all_results:
            for test in result.get("tests", []):
                tests.append(test)
                if test.get("status") == "pass":
                    passed += 1
                elif test.get("status") == "fail":
                    failed += 1
                elif test.get("status") == "skip":
                    skipped += 1
                    
        total = passed + failed + skipped
        
        # Create results summary
        results_summary = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "duration": duration,
                "files_run": len(all_results),
                "run_mode": "parallel" if parallel else "sequential"
            },
            "tests": tests,
            "run_details": {
                "timestamp": get_timestamp(),
                "test_files": test_files
            }
        }
        
        self.test_results = results_summary
        
        self.logger.info(f"Test run completed in {format_duration(duration)}")
        self.logger.info(f"Results: {total} tests, {passed} passed, {failed} failed, {skipped} skipped")
        
        return results_summary
    
    def generate_reports(self, formats: List[str] = None) -> Dict[str, str]:
        """
        Generate reports in specified formats.
        
        Args:
            formats: List of report formats (html, json, markdown, junit)
            
        Returns:
            Dictionary mapping format to report file paths
        """
        if not formats:
            formats = self.config.get("reporting", {}).get("format", ["html"])
            
        title = f"SmartTestAI Test Report - {get_timestamp()}"
        reports = {}
        
        for fmt in formats:
            try:
                if fmt.lower() == "html":
                    file_path = self.report_generator.generate_html_report(self.test_results, title)
                    reports["html"] = file_path
                    self.logger.info(f"Generated HTML report: {file_path}")
                    
                elif fmt.lower() == "json":
                    file_path = self.report_generator.generate_json_report(self.test_results)
                    reports["json"] = file_path
                    self.logger.info(f"Generated JSON report: {file_path}")
                    
                elif fmt.lower() == "junit" or fmt.lower() == "xml":
                    file_path = self.report_generator.generate_junit_report(self.test_results)
                    reports["junit"] = file_path
                    self.logger.info(f"Generated JUnit XML report: {file_path}")
                    
                elif fmt.lower() == "markdown" or fmt.lower() == "md":
                    file_path = self.report_generator.generate_markdown_report(self.test_results, title)
                    reports["markdown"] = file_path
                    self.logger.info(f"Generated Markdown report: {file_path}")
            except Exception as e:
                self.logger.error(f"Error generating {fmt} report: {e}")
                
        return reports
    
    def send_notifications(self, detailed: bool = False) -> None:
        """
        Send notifications with test results.
        
        Args:
            detailed: Whether to include detailed test results in notifications
        """
        summary = {
            "title": f"SmartTestAI Test Results - {get_timestamp()}",
            "total_tests": self.test_results["summary"]["total"],
            "passed_tests": self.test_results["summary"]["passed"],
            "failed_tests": self.test_results["summary"]["failed"],
            "skipped_tests": self.test_results["summary"]["skipped"],
            "duration_seconds": self.test_results["summary"]["duration"],
            "failures": [
                {
                    "name": test.get("name", "Unknown Test"),
                    "message": test.get("error", "No error message")
                }
                for test in self.test_results["tests"]
                if test.get("status") == "fail"
            ]
        }
        
        # Send Slack notification if enabled
        slack_config = self.config.get("notifications", {}).get("slack", {})
        if slack_config.get("enabled", False):
            try:
                self.notification_sender.send_slack_notification(summary, detailed)
                self.logger.info("Sent Slack notification")
            except Exception as e:
                self.logger.error(f"Error sending Slack notification: {e}")
                
        # Send email notification if enabled
        email_config = self.config.get("notifications", {}).get("email", {})
        if email_config.get("enabled", False):
            try:
                self.notification_sender.send_email_notification(summary, detailed)
                self.logger.info("Sent email notification")
            except Exception as e:
                self.logger.error(f"Error sending email notification: {e}")
    
    def generate_test(self, prompt: str, endpoint: str, method: str, 
                     output_dir: str = None, filename: str = None) -> str:
        """
        Generate a test case from a prompt using AI.
        
        Args:
            prompt: Natural language prompt describing the test
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            output_dir: Directory to save generated test
            filename: Name for the test file (without extension)
            
        Returns:
            Path to the generated test file
        """
        # Initialize AI test generator
        openai_config = self.config.get("openai", {})
        generator = TestPromptGenerator(model=openai_config.get("model", "gpt-4"))
        
        self.logger.info(f"Generating test for {method} {endpoint} from prompt")
        
        # Generate test code
        test_code = generator.generate_from_prompt(
            prompt=prompt,
            base_url=self.base_url,
            endpoint=endpoint,
            method=method
        )
        
        # Generate filename if not provided
        if not filename:
            sanitized_endpoint = endpoint.replace("/", "_").strip("_")
            filename = f"test_{method.lower()}_{sanitized_endpoint}"
            
        # Save generated test
        test_file = generator.save_test_to_file(test_code, filename, output_dir)
        self.logger.info(f"Generated test saved to {test_file}")
        
        return test_file


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="SmartTestAI - AI-Powered API Testing Framework")
    
    # Test discovery and execution
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--test-dir", help="Directory to search for tests")
    parser.add_argument("--test-file", help="Specific test file to run")
    parser.add_argument("--all", action="store_true", help="Run all discovered tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially")
    
    # Report options
    parser.add_argument("--report-formats", nargs="+", choices=["html", "json", "junit", "markdown"],
                       help="Report formats to generate")
    
    # Notification options
    parser.add_argument("--notify", action="store_true", help="Send notifications with results")
    parser.add_argument("--detailed-notify", action="store_true", 
                       help="Include detailed results in notifications")
    
    # AI Test Generation
    parser.add_argument("--generate", action="store_true", help="Generate test from prompt")
    parser.add_argument("--prompt", help="Test prompt for AI generation")
    parser.add_argument("--endpoint", help="API endpoint for test generation")
    parser.add_argument("--method", choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
                       help="HTTP method for test generation")
    parser.add_argument("--output-dir", help="Output directory for generated test")
    parser.add_argument("--filename", help="Filename for generated test")
    
    # Misc options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Logging level")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize test runner
    runner = TestRunner(args.config, args.log_level)
    
    # Handle test generation
    if args.generate:
        if not args.prompt or not args.endpoint or not args.method:
            print("Error: --prompt, --endpoint, and --method are required for test generation")
            sys.exit(1)
            
        test_file = runner.generate_test(
            prompt=args.prompt,
            endpoint=args.endpoint,
            method=args.method,
            output_dir=args.output_dir,
            filename=args.filename
        )
        print(f"Generated test saved to {test_file}")
        sys.exit(0)
    
    # Determine which tests to run
    test_files = None
    if args.test_file:
        test_files = [args.test_file]
    elif args.test_dir or args.all:
        test_files = runner.discover_tests(args.test_dir)
        
    # Run tests if specified
    if test_files:
        # Determine parallel mode
        parallel = None
        if args.parallel:
            parallel = True
        elif args.sequential:
            parallel = False
            
        # Run tests
        results = runner.run_tests(test_files, parallel)
        
        # Generate reports
        report_formats = args.report_formats or None
        reports = runner.generate_reports(report_formats)
        
        # Print report paths
        for fmt, path in reports.items():
            print(f"{fmt.upper()} report: {path}")
            
        # Send notifications
        if args.notify or args.detailed_notify:
            runner.send_notifications(args.detailed_notify)
            
        # Exit with appropriate code
        sys.exit(1 if results["summary"]["failed"] > 0 else 0)
    else:
        print("No tests specified to run. Use --test-file, --test-dir, or --all")
        print("Run with --help for usage information")


if __name__ == "__main__":
    main()
