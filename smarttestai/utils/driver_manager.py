"""
Driver manager for handling browser setup and configuration.
"""

import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

logger = logging.getLogger(__name__)


class DriverManager:
    """
    Manages WebDriver instances with configuration-driven setup.
    """
    
    @staticmethod
    def create_driver(config: Optional[Dict[str, Any]] = None) -> webdriver.Chrome:
        """
        Create a WebDriver instance based on configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            WebDriver instance
        """
        if not config:
            # Default Chrome driver
            return webdriver.Chrome()
        
        browser_config = config.get("browser", {})
        browser_type = browser_config.get("default", "chrome").lower()
        
        if browser_type == "chrome":
            return DriverManager._create_chrome_driver(browser_config)
        elif browser_type == "firefox":
            return DriverManager._create_firefox_driver(browser_config)
        else:
            logger.warning(f"Unsupported browser: {browser_type}, falling back to Chrome")
            return DriverManager._create_chrome_driver(browser_config)
    
    @staticmethod
    def _create_chrome_driver(browser_config: Dict[str, Any]) -> webdriver.Chrome:
        """Create Chrome WebDriver with options"""
        options = ChromeOptions()
        
        # Set headless mode
        if browser_config.get("headless", False):
            options.add_argument("--headless")
        
        # Set window size
        window_size = browser_config.get("window_size", "1920,1080")
        options.add_argument(f"--window-size={window_size}")
        
        # Add additional options
        for option in browser_config.get("options", []):
            options.add_argument(option)
        
        logger.info("Creating Chrome WebDriver")
        return webdriver.Chrome(options=options)
    
    @staticmethod
    def _create_firefox_driver(browser_config: Dict[str, Any]) -> webdriver.Firefox:
        """Create Firefox WebDriver with options"""
        options = FirefoxOptions()
        
        # Set headless mode
        if browser_config.get("headless", False):
            options.add_argument("--headless")
        
        logger.info("Creating Firefox WebDriver")
        return webdriver.Firefox(options=options)
