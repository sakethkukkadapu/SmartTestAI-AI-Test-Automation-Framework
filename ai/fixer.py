"""
AI-powered test fixer module that analyzes test failures and suggests or applies fixes.
"""
import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import openai

class TestFixer:
    """Analyzes test failures and suggests/applies fixes using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the test fixer with OpenAI credentials.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY env variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
    
    def analyze_failure(self, test_file: str, error_log: str) -> Dict[str, Any]:
        """
        Analyze a test failure and generate a diagnostic report.
        
        Args:
            test_file: Path to the failed test file
            error_log: Error log or traceback from the test failure
            
        Returns:
            Dictionary with diagnosis and suggested fixes
        """
        # Read the test file
        with open(test_file, 'r') as f:
            test_code = f.read()
        
        system_message = (
            "You are an expert API test troubleshooter. Analyze the given test code and "
            "error logs to determine the cause of the failure. Provide a detailed diagnosis "
            "and suggested fixes."
        )
        
        user_message = f"""
        This test has failed. Please analyze the code and error logs to determine what went wrong.
        
        Test code:
        ```python
        {test_code}
        ```
        
        Error logs:
        ```
        {error_log}
        ```
        
        Provide your diagnosis and suggested fixes in a structured format:
        - Issue: Describe what's causing the test to fail
        - Fix: Provide specific changes needed to fix the test
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        analysis = response.choices[0].message.content
        
        # Extract information from the analysis
        issue_match = re.search(r'Issue:(.*?)(?:Fix:|$)', analysis, re.DOTALL)
        fix_match = re.search(r'Fix:(.*?)(?:$)', analysis, re.DOTALL)
        
        issue = issue_match.group(1).strip() if issue_match else "Unknown issue"
        fix = fix_match.group(1).strip() if fix_match else "No fix suggested"
        
        return {
            "test_file": test_file,
            "issue": issue,
            "suggested_fix": fix,
            "raw_analysis": analysis
        }
    
    def apply_fix(self, test_file: str, error_log: str, 
                  backup: bool = True) -> Tuple[bool, str]:
        """
        Automatically apply fixes to a failed test.
        
        Args:
            test_file: Path to the failed test file
            error_log: Error log or traceback from the test failure
            backup: Whether to create a backup of the original file
            
        Returns:
            Tuple of (success boolean, message)
        """
        # Create backup if requested
        if backup:
            backup_file = f"{test_file}.bak"
            with open(test_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        
        # Read the test file
        with open(test_file, 'r') as f:
            test_code = f.read()
        
        system_message = (
            "You are an expert API test troubleshooter. Fix the given test code based on the "
            "error logs. Only output the corrected Python code with no explanations or "
            "markdown formatting."
        )
        
        user_message = f"""
        This test has failed. Please fix the code based on the error logs.
        
        Test code:
        ```python
        {test_code}
        ```
        
        Error logs:
        ```
        {error_log}
        ```
        
        Return only the fixed Python code without explanations.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        fixed_code = response.choices[0].message.content
        
        # Clean up the code (remove markdown code blocks if present)
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code.split("```python")[1]
        if fixed_code.endswith("```"):
            fixed_code = fixed_code.split("```")[0]
        
        fixed_code = fixed_code.strip()
        
        # Validate the fixed code is valid Python syntax
        try:
            ast.parse(fixed_code)
        except SyntaxError:
            return False, "Generated fix contains syntax errors"
        
        # Write the fixed code back to the file
        with open(test_file, 'w') as f:
            f.write(fixed_code)
            
        return True, f"Fixed test code written to {test_file}"
    
    def suggest_fix_only(self, test_file: str, error_log: str) -> str:
        """
        Suggest fixes without applying them.
        
        Args:
            test_file: Path to the failed test file
            error_log: Error log or traceback from the test failure
            
        Returns:
            String with suggested code changes
        """
        analysis = self.analyze_failure(test_file, error_log)
        
        # Read the test file
        with open(test_file, 'r') as f:
            test_code = f.read()
            
        system_message = (
            "You are an expert API test troubleshooter. Based on the test code and error logs, "
            "provide specific code changes needed to fix the failing test. "
            "Include code diffs showing before and after."
        )
        
        user_message = f"""
        This test has failed. Please suggest specific code changes to fix it.
        
        Test code:
        ```python
        {test_code}
        ```
        
        Error logs:
        ```
        {error_log}
        ```
        
        Issue identified: {analysis['issue']}
        
        Provide the suggested changes in a clear, specific format showing what needs to be changed.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        suggested_changes = response.choices[0].message.content
        return suggested_changes
