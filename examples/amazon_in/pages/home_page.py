"""
Amazon India HomePage - AI-Enhanced Page Object Model
Demonstrates modular architecture without changing core framework
"""

from smarttestai.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class HomePage(BasePage):
    """Amazon India home page with AI-powered self-healing locators"""
    
    def __init__(self, driver):
        super().__init__(driver)
        
        # Register AI-enhanced elements for self-healing
        self.register_ai_element(
            "search_bar",
            "Main search input field where users type product queries",
            [
                (By.ID, "twotabsearchtextbox"),
                (By.NAME, "field-keywords"),
                (By.CSS_SELECTOR, "input[placeholder*='Search']")
            ]
        )
        
        self.register_ai_element(
            "search_button", 
            "Search button or submit button next to search bar",
            [
                (By.ID, "nav-search-submit-button"),
                (By.CSS_SELECTOR, "input[type='submit'][value*='Go']"),
                (By.XPATH, "//input[@type='submit' and contains(@class, 'nav-input')]")
            ]
        )
        
        self.register_ai_element(
            "account_menu",
            "Account and Lists dropdown menu in top navigation",
            [
                (By.ID, "nav-link-accountList"),
                (By.CSS_SELECTOR, "#nav-link-accountList"),
                (By.XPATH, "//span[contains(text(), 'Account & Lists')]")
            ]
        )
        
        self.register_ai_element("cart_button",
            "Shopping cart icon in navigation bar",
            [
                (By.ID, "nav-cart"),
                (By.CSS_SELECTOR, "#nav-cart"),
                (By.XPATH, "//a[contains(@aria-label, 'Cart')]")
            ]
        )
        
        self.register_ai_element(
            "location_selector",
            "Deliver to location selector in top navigation",
            [
                (By.ID, "nav-global-location-slot"),
                (By.CSS_SELECTOR, "#glow-ingress-block"),
                (By.XPATH, "//span[contains(text(), 'Deliver to')]")
            ]
        )
    
    def navigate_to_home(self):
        """Navigate to Amazon India homepage"""
        self.driver.get("https://www.amazon.in")
        return self.wait_for_page_load()
    
    def search_for_product(self, product_name: str):
        """
        Search for a product using AI-enhanced element location
        
        Args:
            product_name: Name of product to search for
            
        Returns:
            bool: True if search was successful
        """
        try:
            # Use AI-enhanced element finding with fallback
            search_box = self.find_element_ai("search_bar")
            if not search_box:
                self.logger.error("Could not locate search bar even with AI assistance")
                return False
            
            # Clear and enter search term
            search_box.clear()
            search_box.send_keys(product_name)
            
            # Submit search - try button first, then Enter key as fallback
            search_button = self.find_element_ai("search_button")
            if search_button:
                search_button.click()
            else:
                search_box.send_keys(Keys.RETURN)
            
            # Wait for search results page to load
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Search failed for '{product_name}': {e}")
            return False
    
    def get_cart_count(self):
        """Get number of items in shopping cart"""
        try:
            cart_element = self.find_element_ai("cart_button")
            if cart_element:
                count_element = cart_element.find_element(By.CSS_SELECTOR, "#nav-cart-count")
                return int(count_element.text) if count_element.text.isdigit() else 0
        except:
            return 0
    
    def select_location(self, location: str = "Mumbai"):
        """
        Select delivery location
        
        Args:
            location: City name for delivery
        """
        try:
            location_element = self.find_element_ai("location_selector")
            if location_element:
                location_element.click()
                # Implementation would continue with location selection modal
                self.logger.info(f"Location selector clicked for: {location}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to select location {location}: {e}")
            return False
    
    def is_prime_member_section_visible(self):
        """Check if Amazon Prime member section is visible"""
        try:
            prime_elements = self.driver.find_elements(
                By.XPATH, "//span[contains(text(), 'Prime') or contains(text(), 'प्राइम')]"
            )
            return len(prime_elements) > 0
        except:
            return False
    
    def get_page_title(self):
        """Get current page title"""
        return self.driver.title
    
    def wait_for_page_load(self, timeout=30):
        """Wait for Amazon homepage to fully load"""
        try:            
            # Wait for key elements to be present
            search_bar = self.find_element_ai("search_bar", timeout=timeout)
            return search_bar is not None
        except:
            return False
