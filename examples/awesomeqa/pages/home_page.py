"""
AwesomeQA Home Page Object
Demonstrates the new modular architecture with AI-enhanced capabilities.
"""

from smarttestai.pages.base_page import BasePage


class HomePage(BasePage):
    """
    Home page of the AwesomeQA e-commerce demo site.
    
    This page object extends the AI-enhanced BasePage and demonstrates
    how to register elements for self-healing locators.
    """
    
    def __init__(self, driver):
        """Initialize the home page with AI element registration"""
        super().__init__(driver)
        
        # Register AI elements for self-healing capabilities
        self.register_ai_element(
            "search_field", 
            "search input field in the header navigation",
            ("id", "search")  # Primary locator as fallback
        )
        
        self.register_ai_element(
            "search_button",
            "search submit button next to search field"
        )
        
        self.register_ai_element(
            "cart_icon",
            "shopping cart icon in header navigation"
        )
        
        self.register_ai_element(
            "user_menu",
            "user account menu or login link in header"
        )
    
    def search_for_product(self, search_term):
        """
        Search for a product using AI-enhanced element interactions.
        
        Args:
            search_term: Product name or keyword to search for
            
        Returns:
            bool: True if search was successful
        """
        if self.type_ai_element("search_field", search_term):
            return self.click_ai_element("search_button")
        return False
    
    def go_to_cart(self):
        """Navigate to shopping cart using AI locator"""
        return self.click_ai_element("cart_icon")
    
    def access_user_menu(self):
        """Access user account menu"""
        return self.click_ai_element("user_menu")
    
    def is_homepage_loaded(self):
        """
        Verify that the homepage has loaded correctly.
        
        Returns:
            bool: True if homepage elements are visible
        """
        return (
            self.is_element_visible_ai("search_field") and
            self.is_element_visible_ai("search_button")
        )
    
    def get_search_suggestions(self):
        """
        Get search suggestions if available.
        This is a placeholder for more advanced AI functionality.
        
        Returns:
            list: List of search suggestions
        """
        # In a full implementation, this could use AI to extract
        # suggestions from the page dynamically
        return []
