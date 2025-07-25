"""
Configuration loader for SmartTestAI framework.
Handles loading and validating YAML configuration files.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Loads and validates test configuration from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader with path to config file.
        
        Args:
            config_path: Path to the config file (defaults to default location)
        """
        if not config_path:
            # Default to the config file in the same directory
            config_path = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary with configuration values
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        return self.config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Key path in dot notation (e.g., "api.base_url")
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            self.load_config()
            
        keys = key_path.split(".")
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_base_url(self) -> str:
        """Get the base URL from config."""
        return self.get_value("api.base_url", "")
    
    def get_timeout(self) -> int:
        """Get the request timeout from config."""
        return self.get_value("api.timeout", 30)
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Get authentication header based on auth configuration.
        
        Returns:
            Dictionary with auth headers
        """
        auth_type = self.get_value("auth.type", "none")
        
        if auth_type == "bearer":
            token = self.get_value("auth.token", "")
            if token:
                return {"Authorization": f"Bearer {token}"}
        
        elif auth_type == "basic":
            username = self.get_value("auth.username", "")
            password = self.get_value("auth.password", "")
            if username and password:
                import base64
                auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
                return {"Authorization": f"Basic {auth_str}"}
        
        elif auth_type == "api_key":
            api_key = self.get_value("auth.api_key", "")
            api_key_name = self.get_value("auth.api_key_name", "X-API-Key")
            if api_key:
                return {api_key_name: api_key}
                
        # Default case - no auth
        return {}
    
    def get_endpoints(self) -> list:
        """Get the list of endpoints from config."""
        return self.get_value("endpoints", [])
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return {
            "model": self.get_value("openai.model", "gpt-4"),
            "temperature": self.get_value("openai.temperature", 0.2),
            "max_tokens": self.get_value("openai.max_tokens", 2048)
        }
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration."""
        return self.get_value("notifications", {})
    
    def get_reporting_config(self) -> Dict[str, Any]:
        """Get reporting configuration."""
        return self.get_value("reporting", {})
