"""
SmartTestAI - AI-Powered Test Automation Framework

A modular, extensible framework for creating intelligent test automation
with self-healing capabilities, visual testing, and AI-driven test generation.
"""

__version__ = "1.0.0"
__author__ = "SmartTestAI Team"

# Core framework imports
from .core.ai_config import AIConfig
from .pages.base_page import BasePage

# Utility imports
from .utils.driver_manager import DriverManager

__all__ = [
    "AIConfig",
    "BasePage", 
    "DriverManager",
]
