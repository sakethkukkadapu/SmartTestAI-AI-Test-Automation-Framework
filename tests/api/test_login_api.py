"""
Example test module for the login endpoint.
"""
import os
import pytest
import requests
import json
from jsonschema import validate

# Import common test utilities
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config_loader import ConfigLoader
from utils.schema_validator import SchemaValidator

# Load configuration
config = ConfigLoader().load_config()
BASE_URL = config.get("api", {}).get("base_url", "https://api.example.com/v1")
AUTH_HEADERS = ConfigLoader().get_auth_header()

# Initialize schema validator
validator = SchemaValidator()

# Define response schemas
LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["token", "user"],
    "properties": {
        "token": {"type": "string"},
        "user": {
            "type": "object",
            "required": ["id", "username", "email"],
            "properties": {
                "id": {"type": "string"},
                "username": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "role": {"type": "string"}
            }
        }
    }
}

LOGIN_ERROR_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {"type": "string"},
        "code": {"type": "integer"}
    }
}


@pytest.fixture
def login_url():
    """Return the login endpoint URL."""
    return f"{BASE_URL}/login"


def test_login_success(login_url):
    """
    Test successful login with valid credentials.
    
    This test verifies that:
    - The login endpoint returns 200 OK
    - The response contains a valid token and user object
    - The response schema matches the expected structure
    """
    # Test data
    payload = {
        "username": "testuser",
        "password": "Password123"
    }
    
    # Send request
    response = requests.post(login_url, json=payload)
    
    # Assertions
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, LOGIN_SUCCESS_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert "token" in data, "Response missing token field"
    assert len(data["token"]) > 0, "Token is empty"
    assert "user" in data, "Response missing user object"
    assert data["user"]["username"] == payload["username"], "Username mismatch"


def test_login_invalid_credentials(login_url):
    """
    Test login with invalid credentials.
    
    This test verifies that:
    - The login endpoint returns 401 Unauthorized
    - The response contains an error message
    - The response schema matches the expected error structure
    """
    # Test data
    payload = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    # Send request
    response = requests.post(login_url, json=payload)
    
    # Assertions
    assert response.status_code == 401, f"Expected 401 Unauthorized but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, LOGIN_ERROR_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert "error" in data, "Response missing error field"
    assert "Invalid credentials" in data["error"], "Unexpected error message"


def test_login_missing_fields(login_url):
    """
    Test login with missing required fields.
    
    This test verifies that:
    - The login endpoint returns 400 Bad Request
    - The response contains an appropriate error message
    - The response schema matches the expected error structure
    """
    # Test data - missing password
    payload = {
        "username": "testuser"
    }
    
    # Send request
    response = requests.post(login_url, json=payload)
    
    # Assertions
    assert response.status_code == 400, f"Expected 400 Bad Request but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, LOGIN_ERROR_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert "error" in data, "Response missing error field"
    assert "password" in data["error"].lower(), "Error should mention missing password field"


def test_login_invalid_method(login_url):
    """
    Test login endpoint with invalid HTTP method.
    
    This test verifies that:
    - Using GET method returns 405 Method Not Allowed
    - The response contains an appropriate error message
    """
    # Send request with GET instead of POST
    response = requests.get(login_url)
    
    # Assertions
    assert response.status_code == 405, f"Expected 405 Method Not Allowed but got {response.status_code}"
