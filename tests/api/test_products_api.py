"""
Example test module for the products endpoint.
"""
import os
import pytest
import requests
from typing import Dict, Any

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

# Define product schemas
PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "price"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "category": {"type": "string"},
        "in_stock": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
    }
}

PRODUCT_LIST_SCHEMA = {
    "type": "object",
    "required": ["products", "page", "total"],
    "properties": {
        "products": {
            "type": "array",
            "items": PRODUCT_SCHEMA
        },
        "page": {"type": "integer", "minimum": 1},
        "page_size": {"type": "integer", "minimum": 1},
        "total": {"type": "integer", "minimum": 0}
    }
}


@pytest.fixture
def products_url():
    """Return the products endpoint URL."""
    return f"{BASE_URL}/products"


@pytest.fixture
def product_data() -> Dict[str, Any]:
    """Test product data fixture."""
    return {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 29.99,
        "category": "test",
        "in_stock": True
    }


def test_get_products_list(products_url):
    """
    Test retrieving a list of products.
    
    This test verifies that:
    - The products endpoint returns 200 OK
    - The response contains a list of products
    - The response schema matches the expected structure
    - Pagination parameters work correctly
    """
    # Test with pagination parameters
    params = {"page": 1, "page_size": 10}
    
    # Send request
    response = requests.get(products_url, params=params, headers=AUTH_HEADERS)
    
    # Assertions
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, PRODUCT_LIST_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert "products" in data, "Response missing products array"
    assert "page" in data, "Response missing page information"
    assert data["page"] == params["page"], "Page parameter not respected"
    if "page_size" in data:
        assert data["page_size"] == params["page_size"], "Page size parameter not respected"


def test_get_product_by_id(products_url):
    """
    Test retrieving a single product by ID.
    
    This test verifies that:
    - The product endpoint returns 200 OK for valid ID
    - The response contains product details
    - The response schema matches the expected structure
    """
    # Assuming product with ID 1 exists
    product_id = "1"
    product_url = f"{products_url}/{product_id}"
    
    # Send request
    response = requests.get(product_url, headers=AUTH_HEADERS)
    
    # Assertions
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, PRODUCT_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert data["id"] == product_id, f"Product ID mismatch, expected {product_id}"


def test_get_product_not_found(products_url):
    """
    Test retrieving a non-existent product.
    
    This test verifies that:
    - The product endpoint returns 404 Not Found for invalid ID
    - The response contains an appropriate error message
    """
    # Use a very large ID that shouldn't exist
    product_id = "999999999"
    product_url = f"{products_url}/{product_id}"
    
    # Send request
    response = requests.get(product_url, headers=AUTH_HEADERS)
    
    # Assertions
    assert response.status_code == 404, f"Expected 404 Not Found but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Additional assertions
    assert "error" in data, "Response missing error field"
    assert "not found" in data["error"].lower(), "Unexpected error message"


def test_create_product(products_url, product_data):
    """
    Test creating a new product.
    
    This test verifies that:
    - The products endpoint returns 201 Created
    - The response contains the created product with an ID
    - The response schema matches the expected structure
    """
    # Send request
    response = requests.post(products_url, json=product_data, headers=AUTH_HEADERS)
    
    # Assertions
    assert response.status_code == 201, f"Expected 201 Created but got {response.status_code}"
    
    # Parse response
    data = response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(data, PRODUCT_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert "id" in data, "Response missing ID for created product"
    assert data["name"] == product_data["name"], "Product name mismatch"
    assert data["price"] == product_data["price"], "Product price mismatch"
    
    # Clean up - delete the created product
    delete_url = f"{products_url}/{data['id']}"
    requests.delete(delete_url, headers=AUTH_HEADERS)


def test_update_product(products_url, product_data):
    """
    Test updating an existing product.
    
    This test verifies that:
    - First creates a product to update
    - The PUT endpoint returns 200 OK
    - The response contains the updated product
    - The product details are correctly updated
    """
    # First create a product
    create_response = requests.post(products_url, json=product_data, headers=AUTH_HEADERS)
    assert create_response.status_code == 201, "Failed to create test product for update test"
    
    created_product = create_response.json()
    product_id = created_product["id"]
    
    # Update data
    update_data = product_data.copy()
    update_data["name"] = "Updated Product Name"
    update_data["price"] = 39.99
    
    # Send update request
    update_url = f"{products_url}/{product_id}"
    update_response = requests.put(update_url, json=update_data, headers=AUTH_HEADERS)
    
    # Assertions
    assert update_response.status_code == 200, f"Expected 200 OK but got {update_response.status_code}"
    
    # Parse response
    updated_product = update_response.json()
    
    # Schema validation
    validation_result = validator.validate_response_safe(updated_product, PRODUCT_SCHEMA)
    assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    # Additional assertions
    assert updated_product["id"] == product_id, "Product ID changed after update"
    assert updated_product["name"] == update_data["name"], "Product name not updated"
    assert updated_product["price"] == update_data["price"], "Product price not updated"
    
    # Clean up - delete the product
    delete_url = f"{products_url}/{product_id}"
    requests.delete(delete_url, headers=AUTH_HEADERS)


def test_delete_product(products_url, product_data):
    """
    Test deleting a product.
    
    This test verifies that:
    - First creates a product to delete
    - The DELETE endpoint returns 204 No Content
    - The product is actually deleted (404 when trying to fetch it)
    """
    # First create a product
    create_response = requests.post(products_url, json=product_data, headers=AUTH_HEADERS)
    assert create_response.status_code == 201, "Failed to create test product for delete test"
    
    product_id = create_response.json()["id"]
    delete_url = f"{products_url}/{product_id}"
    
    # Send delete request
    delete_response = requests.delete(delete_url, headers=AUTH_HEADERS)
    
    # Assertions
    assert delete_response.status_code == 204, f"Expected 204 No Content but got {delete_response.status_code}"
    
    # Verify product is deleted by trying to fetch it
    get_response = requests.get(delete_url, headers=AUTH_HEADERS)
    assert get_response.status_code == 404, "Product still exists after deletion"
