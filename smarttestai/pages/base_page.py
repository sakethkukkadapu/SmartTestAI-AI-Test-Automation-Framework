"""
Base page class with AI-enhanced capabilities.
This class provides the foundation for all page objects with self-healing locators,
AI-powered element interactions, and visual testing integration.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base page class with AI-enhanced capabilities for self-healing locators,
    intelligent element interactions, and visual verification.
    """
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the base page with AI capabilities.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # AI element registry for self-healing
        self._ai_elements = {}
        
        # Load configuration
        from smarttestai.core.ai_config import AIConfig
        self.config = AIConfig
        
        # Base URL from configuration
        self.base_url = self.config.get("suite_info.base_url", "")
        
        logger.debug(f"Initialized {self.__class__.__name__} with AI capabilities")
    
    def register_ai_element(self, name: str, description: str, primary_locator: Optional[Tuple[str, str]] = None):
        """
        Register an element for AI-powered self-healing.
        
        Args:
            name: Unique name for the element
            description: Human-readable description for AI identification
            primary_locator: Optional tuple of (strategy, value) for primary locator
        """
        self._ai_elements[name] = {
            "description": description,
            "primary_locator": primary_locator,
            "healing_history": []
        }
        logger.debug(f"Registered AI element: {name} - {description}")
    
    def find_element_ai(self, element_name: str) -> Optional[WebElement]:
        """
        Find an element using AI-powered self-healing.
        
        Args:
            element_name: Name of the registered AI element
            
        Returns:
            WebElement if found, None otherwise
        """
        if element_name not in self._ai_elements:
            logger.error(f"Element '{element_name}' not registered for AI healing")
            return None
        
        element_info = self._ai_elements[element_name]
        
        # Try primary locator first if available
        if element_info.get("primary_locator"):
            try:
                strategy, value = element_info["primary_locator"]
                return self.driver.find_element(getattr(By, strategy.upper()), value)
            except Exception as e:
                logger.debug(f"Primary locator failed for {element_name}: {e}")
        
        # If AI healing is disabled, return None
        if not self.config.is_feature_enabled("self_healing"):
            logger.warning(f"Self-healing disabled, cannot find element: {element_name}")
            return None
        
        # Use AI-powered healing (placeholder implementation)
        return self._heal_element(element_name, element_info)
    
    def _heal_element(self, element_name: str, element_info: Dict[str, Any]) -> Optional[WebElement]:
        """
        Use AI to find an element when primary locators fail.
        
        This is a placeholder implementation. In a full implementation, this would:
        1. Take a screenshot of the current page
        2. Use AI to analyze the page and find elements matching the description
        3. Return the best matching element
        
        Args:
            element_name: Name of the element to heal
            element_info: Element information including description
            
        Returns:
            WebElement if healing successful, None otherwise
        """
        logger.info(f"Attempting AI healing for element: {element_name}")
        
        try:
            # Placeholder: Try common locator strategies
            description = element_info["description"].lower()
            
            # Try to find by text content
            if "button" in description:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if any(word in btn.text.lower() for word in description.split() if len(word) > 2):
                        logger.info(f"Healed element {element_name} using text matching")
                        return btn
            
            # Try to find by common attributes
            if "input" in description or "field" in description:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    placeholder = inp.get_attribute("placeholder") or ""
                    if any(word in placeholder.lower() for word in description.split() if len(word) > 2):
                        logger.info(f"Healed element {element_name} using placeholder matching")
                        return inp
            
            logger.warning(f"Could not heal element: {element_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error during element healing for {element_name}: {e}")
            return None
    
    def click_ai_element(self, element_name: str) -> bool:
        """
        Click an AI-registered element with self-healing.
        
        Args:
            element_name: Name of the registered element
            
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element_ai(element_name)
        if element:
            try:
                element.click()
                logger.debug(f"Successfully clicked element: {element_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to click element {element_name}: {e}")
                return False
        else:
            logger.error(f"Could not find element to click: {element_name}")
            return False
    
    def type_ai_element(self, element_name: str, text: str) -> bool:
        """
        Type text into an AI-registered element with self-healing.
        
        Args:
            element_name: Name of the registered element
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element_ai(element_name)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.debug(f"Successfully typed into element: {element_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to type into element {element_name}: {e}")
                return False
        else:
            logger.error(f"Could not find element to type into: {element_name}")
            return False
    
    def is_element_visible_ai(self, element_name: str) -> bool:
        """
        Check if an AI-registered element is visible.
        
        Args:
            element_name: Name of the registered element
            
        Returns:
            True if visible, False otherwise
        """
        element = self.find_element_ai(element_name)
        if element:
            try:
                return element.is_displayed()
            except Exception as e:
                logger.debug(f"Error checking visibility of {element_name}: {e}")
                return False
        return False
    
    def open(self, path: str = "") -> None:
        """
        Open the page at the specified path.
        
        Args:
            path: Path to append to base URL
        """
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}" if path else self.base_url
        logger.info(f"Opening page: {url}")
        self.driver.get(url)
    
    def get_page_title(self) -> str:
        """Get the current page title"""
        return self.driver.title
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """
        Wait for page to load completely.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if page loaded, False if timeout
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except Exception as e:
            logger.warning(f"Page load timeout: {e}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the saved screenshot
        """
        if not filename:
            import time
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        # Create screenshots directory if it doesn't exist
        from pathlib import Path
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        screenshot_path = screenshots_dir / filename
        self.driver.save_screenshot(str(screenshot_path))
        
        logger.debug(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)
    
    def scroll_to_element(self, element: WebElement) -> None:
        """Scroll to bring an element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
    
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = 10) -> WebElement:
        """
        Wait for an element to be visible.
        
        Args:
            locator: Tuple of (strategy, value)
            timeout: Maximum time to wait
            
        Returns:
            WebElement when visible
        """
        strategy, value = locator
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((getattr(By, strategy.upper()), value))
        )
    
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = 10) -> WebElement:
        """
        Wait for an element to be clickable.
        
        Args:
            locator: Tuple of (strategy, value)
            timeout: Maximum time to wait
            
        Returns:
            WebElement when clickable
        """
        strategy, value = locator
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((getattr(By, strategy.upper()), value))
        )
