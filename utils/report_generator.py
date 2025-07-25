"""
Report generator module for SmartTestAI framework.
Generates HTML and JSON reports from test results.
"""
import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

class ReportGenerator:
    """Generates reports from test results in various formats."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports (default: ./reports)
        """
        self.output_dir = output_dir or './reports'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_html_report(self, test_results: Dict[str, Any], 
                            title: str = "SmartTestAI Test Report") -> str:
        """
        Generate an HTML report from test results.
        
        Args:
            test_results: Dictionary with test results
            title: Report title
            
        Returns:
            Path to the generated HTML report
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"
        file_path = os.path.join(self.output_dir, filename)
        
        # Extract results
        total_tests = test_results.get("summary", {}).get("total", 0)
        passed = test_results.get("summary", {}).get("passed", 0)
        failed = test_results.get("summary", {}).get("failed", 0)
        skipped = test_results.get("summary", {}).get("skipped", 0)
        duration = test_results.get("summary", {}).get("duration", 0)
        tests = test_results.get("tests", [])
        
        # Calculate pass percentage
        pass_percentage = 0
        if total_tests > 0:
            pass_percentage = (passed / total_tests) * 100
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f7f9fc;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
        }}
        h1 {{
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .summary {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        .summary-box {{
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            margin: 0 10px 10px 0;
            text-align: center;
            min-width: 150px;
        }}
        .total {{
            background-color: #f1f8ff;
            border-left: 5px solid #4a69bd;
        }}
        .passed {{
            background-color: #e8f5e9;
            border-left: 5px solid #4CAF50;
        }}
        .failed {{
            background-color: #ffebee;
            border-left: 5px solid #f44336;
        }}
        .skipped {{
            background-color: #fff8e1;
            border-left: 5px solid #ffb300;
        }}
        .time {{
            background-color: #f3e5f5;
            border-left: 5px solid #8e24aa;
        }}
        .test-results {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }}
        .test-results th, .test-results td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        .test-results th {{
            background-color: #f8f9fa;
        }}
        .test-results tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .test-results tr:hover {{
            background-color: #f2f2f2;
        }}
        .status-pass {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-fail {{
            color: #f44336;
            font-weight: bold;
        }}
        .status-skip {{
            color: #ffb300;
            font-weight: bold;
        }}
        .error-details {{
            background-color: #fff8f8;
            border-left: 4px solid #f44336;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        footer {{
            margin-top: 30px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="summary">
            <div class="summary-box total">
                <h3>Total Tests</h3>
                <p>{total_tests}</p>
            </div>
            <div class="summary-box passed">
                <h3>Passed</h3>
                <p>{passed} ({pass_percentage:.1f}%)</p>
            </div>
            <div class="summary-box failed">
                <h3>Failed</h3>
                <p>{failed}</p>
            </div>
            <div class="summary-box skipped">
                <h3>Skipped</h3>
                <p>{skipped}</p>
            </div>
            <div class="summary-box time">
                <h3>Duration</h3>
                <p>{duration:.2f}s</p>
            </div>
        </div>

        <h2>Test Details</h2>
        <table class="test-results">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, test in enumerate(tests):
            test_name = test.get("name", f"Test {i+1}")
            status = test.get("status", "")
            test_duration = test.get("duration", 0)
            details = test.get("details", "")
            error = test.get("error", "")
            
            status_class = ""
            if status.lower() == "pass":
                status_class = "status-pass"
            elif status.lower() == "fail":
                status_class = "status-fail"
            elif status.lower() == "skip":
                status_class = "status-skip"
            
            html_content += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{test_name}</td>
                    <td class="{status_class}">{status.upper()}</td>
                    <td>{test_duration:.2f}s</td>
                    <td>
                        {details}
                        {f'<div class="error-details">{error}</div>' if error else ''}
                    </td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        
        <footer>
            <p>Generated by SmartTestAI on """ + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + """</p>
        </footer>
    </div>
</body>
</html>
        """
        
        # Write HTML to file
        with open(file_path, "w") as f:
            f.write(html_content)
            
        return file_path
    
    def generate_json_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate a JSON report from test results.
        
        Args:
            test_results: Dictionary with test results
            
        Returns:
            Path to the generated JSON report
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        file_path = os.path.join(self.output_dir, filename)
        
        # Add metadata
        report_data = test_results.copy()
        report_data["metadata"] = {
            "generated_at": datetime.datetime.now().isoformat(),
            "generator": "SmartTestAI Report Generator"
        }
        
        # Write JSON to file
        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2)
            
        return file_path
    
    def generate_junit_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate a JUnit XML report from test results.
        
        Args:
            test_results: Dictionary with test results
            
        Returns:
            Path to the generated XML report
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.xml"
        file_path = os.path.join(self.output_dir, filename)
        
        # Extract results
        tests = test_results.get("tests", [])
        total_tests = test_results.get("summary", {}).get("total", 0)
        failures = test_results.get("summary", {}).get("failed", 0)
        skipped = test_results.get("summary", {}).get("skipped", 0)
        duration = test_results.get("summary", {}).get("duration", 0)
        
        # Create XML structure
        test_suite = ET.Element("testsuite")
        test_suite.set("name", "SmartTestAI Tests")
        test_suite.set("tests", str(total_tests))
        test_suite.set("failures", str(failures))
        test_suite.set("skips", str(skipped))
        test_suite.set("time", str(duration))
        test_suite.set("timestamp", datetime.datetime.now().isoformat())
        
        # Add test cases
        for test in tests:
            test_case = ET.SubElement(test_suite, "testcase")
            test_case.set("name", test.get("name", "Unknown Test"))
            test_case.set("classname", test.get("classname", "APITest"))
            test_case.set("time", str(test.get("duration", 0)))
            
            status = test.get("status", "").lower()
            if status == "fail":
                failure = ET.SubElement(test_case, "failure")
                failure.set("message", test.get("message", "Test failed"))
                failure.set("type", test.get("error_type", "AssertionError"))
                failure.text = test.get("error", "")
            elif status == "skip":
                skipped_el = ET.SubElement(test_case, "skipped")
                skipped_el.set("message", test.get("message", "Test skipped"))
        
        # Convert to string and pretty print
        xml_str = ET.tostring(test_suite, encoding="utf-8")
        parsed_xml = minidom.parseString(xml_str)
        pretty_xml = parsed_xml.toprettyxml(indent="  ")
        
        # Write to file
        with open(file_path, "w") as f:
            f.write(pretty_xml)
            
        return file_path
    
    def generate_markdown_report(self, test_results: Dict[str, Any], 
                                title: str = "SmartTestAI Test Report") -> str:
        """
        Generate a Markdown report from test results.
        
        Args:
            test_results: Dictionary with test results
            title: Report title
            
        Returns:
            Path to the generated Markdown report
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.md"
        file_path = os.path.join(self.output_dir, filename)
        
        # Extract results
        total_tests = test_results.get("summary", {}).get("total", 0)
        passed = test_results.get("summary", {}).get("passed", 0)
        failed = test_results.get("summary", {}).get("failed", 0)
        skipped = test_results.get("summary", {}).get("skipped", 0)
        duration = test_results.get("summary", {}).get("duration", 0)
        tests = test_results.get("tests", [])
        
        # Calculate pass percentage
        pass_percentage = 0
        if total_tests > 0:
            pass_percentage = (passed / total_tests) * 100
            
        # Generate markdown content
        md_content = f"# {title}\n\n"
        md_content += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "## Summary\n\n"
        md_content += f"- **Total Tests:** {total_tests}\n"
        md_content += f"- **Passed:** {passed} ({pass_percentage:.1f}%)\n"
        md_content += f"- **Failed:** {failed}\n"
        md_content += f"- **Skipped:** {skipped}\n"
        md_content += f"- **Duration:** {duration:.2f} seconds\n\n"
        
        md_content += "## Test Details\n\n"
        md_content += "| # | Test Name | Status | Duration | Details |\n"
        md_content += "|---|-----------|--------|----------|--------|\n"
        
        for i, test in enumerate(tests):
            test_name = test.get("name", f"Test {i+1}")
            status = test.get("status", "")
            test_duration = test.get("duration", 0)
            details = test.get("details", "").replace("\n", "<br>")
            
            status_formatted = status.upper()
            if status.lower() == "pass":
                status_formatted = "✅ PASS"
            elif status.lower() == "fail":
                status_formatted = "❌ FAIL"
            elif status.lower() == "skip":
                status_formatted = "⚠️ SKIP"
                
            md_content += f"| {i+1} | {test_name} | {status_formatted} | {test_duration:.2f}s | {details} |\n"
            
            if status.lower() == "fail" and test.get("error"):
                md_content += f"\n<details><summary>Error Details</summary>\n\n```\n{test.get('error')}\n```\n\n</details>\n\n"
        
        md_content += "\n---\n*Generated by SmartTestAI - Automated Testing Framework*"
        
        # Write to file
        with open(file_path, "w") as f:
            f.write(md_content)
            
        return file_path
