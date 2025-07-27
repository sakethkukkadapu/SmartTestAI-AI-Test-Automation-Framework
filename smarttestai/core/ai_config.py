"""
Dynamic configuration system for SmartTestAI framework.
Supports YAML-based suite configurations with environment variable overrides.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors"""
    pass


class AIConfig:
    """
    Dynamic configuration loader that supports:
    - Suite-specific YAML configurations
    - Environment variable overrides
    - Feature toggles for AI capabilities
    - Performance and cost optimization settings
    """
    
    # Class variables for configuration management
    _config_cache = {}
    _current_suite = None
    _current_config = None
    logger = logging.getLogger(__name__)
    
    # Default configuration values
    _defaults = {
        'ai_features': {
            'self_healing': True,
            'visual_testing': True,
            'test_generation': True,
            'test_analysis': True,
        },
        'ai_settings': {
            'model': 'models/gemini-2.5-flash-lite',
            'fallback_models': ['models/gemini-2.0-pro'],
            'max_retries': 3,
            'initial_retry_delay': 2.0,
            'max_retry_delay': 60,
            'rate_limit_codes': [429, 503],
            'enable_caching': True,
            'cache_ttl': 3600,
            'visual_threshold': 0.9,
            'temperature': 0.3,
            'top_p': 0.9,
            'max_tokens': 2048,
        },
        'browser': {
            'default': 'chrome',
            'headless': False,
            'window_size': '1920,1080',
            'timeout': 30,
        },
        'test_execution': {
            'parallel': False,
            'max_workers': 4,
            'timeout': 300,
        }
    }
    
    _current_config = None
    _current_suite = None
    
    @classmethod
    def load_suite_config(cls, suite_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration for a specific test suite.
        
        Args:
            suite_name: Name of the test suite
            config_path: Optional path to config file. If not provided, 
                        looks for examples/{suite_name}/config.yaml
        
        Returns:
            Dictionary containing the loaded configuration
        """
        if not config_path:
            # Default path: examples/{suite_name}/config.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "examples" / suite_name / "config.yaml"
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(f"Config not found for suite: {suite_name} at {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # Validate required configuration sections
            cls._validate_config(config, suite_name)
            
            # Merge with defaults (loaded config takes precedence)
            config = cls._deep_merge(cls._defaults.copy(), config)
            logger.info(f"Loaded configuration from: {config_path}")
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config for suite '{suite_name}': {e}")
        
        # Apply environment variable overrides
        config = cls._apply_env_overrides(config)
        
        # Store configuration in cache and set as current
        cls._config_cache[suite_name] = config
        cls._current_config = config
        cls._current_suite = suite_name
        
        return config
    
    @classmethod
    def _deep_merge(cls, base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def _apply_env_overrides(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        
        # AI Settings overrides
        if os.getenv('GOOGLE_API_KEY'):
            config.setdefault('ai_settings', {})['api_key'] = os.getenv('GOOGLE_API_KEY')
        
        if os.getenv('GOOGLE_AI_MODEL'):
            config.setdefault('ai_settings', {})['model'] = os.getenv('GOOGLE_AI_MODEL')
        
        if os.getenv('VISUAL_THRESHOLD'):
            config.setdefault('ai_settings', {})['visual_threshold'] = float(os.getenv('VISUAL_THRESHOLD'))
        
        if os.getenv('AI_FEATURES_ENABLED'):
            enabled = os.getenv('AI_FEATURES_ENABLED').lower() == 'true'
            for feature in config.get('ai_features', {}):
                config['ai_features'][feature] = enabled
        
        # Browser settings overrides
        if os.getenv('BROWSER'):
            config.setdefault('browser', {})['default'] = os.getenv('BROWSER')
        
        if os.getenv('HEADLESS'):
            config.setdefault('browser', {})['headless'] = os.getenv('HEADLESS').lower() == 'true'
        
        return config
    
    @classmethod
    def _validate_config(cls, config: Dict, suite: str) -> None:
        """Validate that required configuration sections exist"""
        required_sections = ['suite_info', 'ai_features']
        required_ai_settings = ['model']
        
        # Check required top-level sections
        missing_sections = [section for section in required_sections if section not in config]
        if missing_sections:
            raise ConfigurationError(f"Missing required config sections for suite '{suite}': {missing_sections}")
        
        # Validate suite_info
        suite_info = config.get('suite_info', {})
        if not suite_info.get('name'):
            raise ConfigurationError(f"Suite '{suite}' missing required 'name' in suite_info")
        
        # Validate AI settings if present
        ai_settings = config.get('ai_settings', {})
        missing_ai_settings = [setting for setting in required_ai_settings 
                             if setting not in ai_settings and setting not in cls._defaults['ai_settings']]
        if missing_ai_settings:
            raise ConfigurationError(f"Suite '{suite}' missing required AI settings: {missing_ai_settings}")
        
        # Validate feature toggles are boolean
        ai_features = config.get('ai_features', {})
        for feature, enabled in ai_features.items():
            if not isinstance(enabled, bool):
                raise ConfigurationError(f"AI feature '{feature}' must be boolean, got {type(enabled).__name__}")
    
    @classmethod
    def get(cls, key: str, default=None, suite: str = None):
        """Get configuration value using dot notation with type safety"""
        # Use current suite if none specified
        if suite is None:
            suite = cls._current_suite
        config = cls._get_suite_config(suite)
        
        # Navigate nested dictionary using dot notation
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
        except (KeyError, TypeError) as e:
            cls.logger.debug(f"Config key '{key}' not found or invalid: {e}")
            return default
    
    @classmethod
    def _get_suite_config(cls, suite: str) -> Dict:
        """Get the configuration for a suite"""
        config = cls._config_cache.get(suite)
        if not config:
            raise ConfigurationError(f"Suite '{suite}' not loaded. Call load_suite_config() first.")
        return config
    
    @classmethod
    def is_feature_enabled(cls, feature_name: str, suite: str = None) -> bool:
        """Check if an AI feature is enabled"""
        # Use current suite if none specified
        if suite is None:
            suite = cls._current_suite
        return cls.get(f'ai_features.{feature_name}', False, suite)
    
    @classmethod
    def get_current_suite(cls) -> Optional[str]:
        """Get the name of the currently loaded suite"""
        return cls._current_suite
    
    @classmethod
    def get_all_config(cls, suite: str = None) -> Dict[str, Any]:
        """Get the complete current configuration"""
        # Use current suite if none specified
        if suite is None:
            suite = cls._current_suite
        config = cls._get_suite_config(suite)
        return config.copy() if config else {}
    
    # Legacy compatibility properties for existing code
    @property
    def DEFAULT_MODEL(self) -> str:
        return self.get('ai_settings.model', 'models/gemini-2.5-flash-lite')
    
    @property
    def FALLBACK_MODELS(self) -> list:
        return self.get('ai_settings.fallback_models', ['models/gemini-2.0-pro'])
    
    @property
    def MAX_RETRIES(self) -> int:
        return self.get('ai_settings.max_retries', 3)
    
    @property
    def INITIAL_RETRY_DELAY(self) -> float:
        return self.get('ai_settings.initial_retry_delay', 2.0)
    
    @property
    def MAX_RETRY_DELAY(self) -> int:
        return self.get('ai_settings.max_retry_delay', 60)
    
    @property
    def RATE_LIMIT_CODES(self) -> list:
        return self.get('ai_settings.rate_limit_codes', [429, 503])
    
    @property
    def VISUAL_TESTING_ENABLED(self) -> bool:
        return self.is_feature_enabled('visual_testing')
    
    @property
    def SELF_HEALING_ENABLED(self) -> bool:
        return self.is_feature_enabled('self_healing')


# Create a default instance for backward compatibility
_default_instance = AIConfig()

# Expose class methods as module-level functions for convenience
load_suite_config = AIConfig.load_suite_config
get_config = AIConfig.get
is_feature_enabled = AIConfig.is_feature_enabled
