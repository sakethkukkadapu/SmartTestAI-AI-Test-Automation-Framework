"""
AI-powered test generation module that uses OpenAI's GPT to generate test cases
from natural language or OpenAPI specifications.
"""
import os
import json
import yaml
import openai
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

class TestPromptGenerator:
    """Generates test cases from natural language prompts or API docs using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the prompt generator with OpenAI credentials.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY env variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
    
    def generate_from_prompt(self, prompt: str, base_url: str, 
                             endpoint: str, method: str) -> str:
        """
        Generate a test case from a natural language prompt.
        
        Args:
            prompt: Natural language description of the test case
            base_url: Base URL for the API
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            
        Returns:
            Generated Python test code as a string
        """
        system_message = (
            "You are an expert API test developer. Generate a pytest-compatible "
            "test function that validates the specified scenario. "
            "Only output valid Python code with no explanations or markdown formatting."
        )
        
        user_message = f"""
        Create a test case for the {method} {endpoint} endpoint with the following scenario:
        
        {prompt}
        
        Use these guidelines:
        - Use requests library for HTTP calls
        - Import required libraries at the top
        - Base URL variable is BASE_URL = "{base_url}"
        - Include appropriate assertions to validate the scenario
        - Function should be named test_<descriptive_name>
        - Add docstring explaining test purpose
        - Handle authentication if needed
        - Include proper error handling
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the code from the response
        test_code = response.choices[0].message.content
        
        # Clean up the code (remove markdown code blocks if present)
        if test_code.startswith("```python"):
            test_code = test_code.split("```python")[1]
        if test_code.endswith("```"):
            test_code = test_code.split("```")[0]
            
        return test_code.strip()
    
    def generate_from_openapi(self, spec_path: str, endpoint: str, 
                             method: str, scenario: str) -> str:
        """
        Generate a test case from OpenAPI/Swagger specification.
        
        Args:
            spec_path: Path to OpenAPI spec file (JSON or YAML)
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            scenario: Description of the test scenario
            
        Returns:
            Generated Python test code as a string
        """
        # Read OpenAPI spec file
        spec_data = self._read_spec_file(spec_path)
        
        # Extract endpoint information from spec
        endpoint_info = self._extract_endpoint_info(spec_data, endpoint, method)
        
        if not endpoint_info:
            raise ValueError(f"Endpoint {method} {endpoint} not found in OpenAPI spec")
        
        # Create a prompt with the OpenAPI spec information
        prompt = f"""
        Create a test case for the {method} {endpoint} endpoint with the following scenario:
        {scenario}
        
        Endpoint details from OpenAPI spec:
        - Description: {endpoint_info.get('description', 'No description')}
        - Parameters: {json.dumps(endpoint_info.get('parameters', []))}
        - Request body: {json.dumps(endpoint_info.get('requestBody', {}))}
        - Responses: {json.dumps(endpoint_info.get('responses', {}))}
        
        Use these guidelines:
        - Import required libraries
        - Use requests library for HTTP calls
        - Include appropriate assertions to validate the scenario
        - Function should be named test_<descriptive_name>
        - Add docstring explaining test purpose
        """
        
        # Generate test code using the custom prompt
        return self.generate_from_prompt(
            prompt=prompt,
            base_url=spec_data.get('servers', [{}])[0].get('url', 'http://localhost'),
            endpoint=endpoint,
            method=method
        )
    
    def save_test_to_file(self, test_code: str, filename: str, 
                          output_dir: str = None) -> str:
        """
        Save generated test code to a file.
        
        Args:
            test_code: Generated test code
            filename: Name for the test file (without extension)
            output_dir: Directory to save the file (defaults to tests/generated)
            
        Returns:
            Path to the saved file
        """
        if not output_dir:
            output_dir = Path(__file__).parent.parent / "tests" / "generated"
        else:
            output_dir = Path(output_dir)
            
        # Create directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure filename has proper format
        if not filename.startswith("test_"):
            filename = f"test_{filename}"
        if not filename.endswith(".py"):
            filename = f"{filename}.py"
            
        file_path = output_dir / filename
        
        with open(file_path, "w") as f:
            f.write(test_code)
            
        return str(file_path)
    
    def _read_spec_file(self, spec_path: str) -> Dict[str, Any]:
        """Read and parse an OpenAPI specification file."""
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.json'):
                return json.load(f)
            elif spec_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f)
            else:
                raise ValueError("Unsupported specification file format. Use JSON or YAML.")
    
    def _extract_endpoint_info(self, spec_data: Dict[str, Any], 
                              endpoint: str, method: str) -> Dict[str, Any]:
        """Extract endpoint information from OpenAPI spec."""
        paths = spec_data.get('paths', {})
        endpoint_data = paths.get(endpoint, {})
        method_data = endpoint_data.get(method.lower(), {})
        
        return method_data
