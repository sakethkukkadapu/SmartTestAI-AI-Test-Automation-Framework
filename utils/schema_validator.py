"""
JSON Schema validator utility for API response validation.
"""
import json
import jsonschema
from jsonschema import validate, ValidationError
from typing import Any, Dict, List, Union, Optional

class SchemaValidator:
    """Validates API responses against JSON schemas."""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """
        Initialize the schema validator.
        
        Args:
            schema_dir: Directory containing schema files (optional)
        """
        self.schema_dir = schema_dir
        self.schema_cache: Dict[str, Dict[str, Any]] = {}
        
    def validate_response(self, response_data: Any, schema: Union[Dict[str, Any], str]) -> bool:
        """
        Validate a response against a schema.
        
        Args:
            response_data: Response data to validate
            schema: Schema as dict or path to schema file
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        # If schema is a string, it's a file path
        if isinstance(schema, str):
            schema_dict = self._load_schema(schema)
        else:
            schema_dict = schema
            
        validate(instance=response_data, schema=schema_dict)
        return True
        
    def validate_response_safe(self, response_data: Any, 
                              schema: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Validate a response against a schema, returning errors instead of raising.
        
        Args:
            response_data: Response data to validate
            schema: Schema as dict or path to schema file
            
        Returns:
            Dict with validation result: {"valid": bool, "errors": list}
        """
        result = {
            "valid": True,
            "errors": []
        }
        
        try:
            self.validate_response(response_data, schema)
        except ValidationError as e:
            result["valid"] = False
            result["errors"] = [
                {
                    "message": e.message,
                    "path": ".".join(str(p) for p in e.path) if e.path else "",
                    "schema_path": ".".join(str(p) for p in e.schema_path) if e.schema_path else "",
                }
            ]
        except Exception as e:
            result["valid"] = False
            result["errors"] = [{"message": str(e), "path": "", "schema_path": ""}]
            
        return result
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """
        Load a schema from file with caching.
        
        Args:
            schema_path: Path to the schema file
            
        Returns:
            Schema as dict
        """
        if schema_path in self.schema_cache:
            return self.schema_cache[schema_path]
            
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        self.schema_cache[schema_path] = schema
        return schema
    
    def generate_schema_from_example(self, example_data: Any) -> Dict[str, Any]:
        """
        Generate a JSON schema from example data.
        
        Args:
            example_data: Example JSON data
            
        Returns:
            Generated JSON schema
        """
        schema: Dict[str, Any] = {"type": "object", "properties": {}}
        
        if isinstance(example_data, dict):
            schema["type"] = "object"
            schema["properties"] = {}
            
            for key, value in example_data.items():
                schema["properties"][key] = self._infer_type_schema(value)
                
        elif isinstance(example_data, list):
            schema["type"] = "array"
            if example_data:
                # Use the first item to infer array item type
                schema["items"] = self._infer_type_schema(example_data[0])
                
        else:
            schema = self._infer_type_schema(example_data)
            
        return schema
        
    def _infer_type_schema(self, value: Any) -> Dict[str, Any]:
        """Infer schema type from a value."""
        if value is None:
            return {"type": "null"}
            
        elif isinstance(value, bool):
            return {"type": "boolean"}
            
        elif isinstance(value, int):
            return {"type": "integer"}
            
        elif isinstance(value, float):
            return {"type": "number"}
            
        elif isinstance(value, str):
            return {"type": "string"}
            
        elif isinstance(value, list):
            if not value:
                return {"type": "array", "items": {}}
            else:
                return {"type": "array", "items": self._infer_type_schema(value[0])}
                
        elif isinstance(value, dict):
            properties = {}
            for k, v in value.items():
                properties[k] = self._infer_type_schema(v)
                
            return {"type": "object", "properties": properties}
            
        # Default fallback
        return {"type": "string"}
