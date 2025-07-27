"""
Amazon India Test Suite - Demonstrates Modular Architecture
Created in < 2 minutes using SmartTestAI framework templates
"""

import pytest
from selenium import webdriver
from smarttestai.utils.driver_manager import DriverManager
from smarttestai.core.ai_config import AIConfig
from examples.amazon_in.pages.home_page import HomePage


class TestAmazonHomePage:
    """Test suite for Amazon India homepage functionality"""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request):
        """Load Amazon India suite configuration before any tests"""
        try:
            config = AIConfig.load_suite_config("amazon_in")
            # Store config in class for access by other fixtures
            request.cls.suite_config = config
            print(f"✅ Loaded configuration for Amazon India test suite")
        except Exception as e:
            pytest.fail(f"Failed to load suite configuration: {e}")
    
    @pytest.fixture(scope="function")
    def driver(self):
        """Create WebDriver instance for each test"""
        driver_manager = DriverManager()
        driver = driver_manager.create_driver()
        yield driver
        driver.quit()
    
    @pytest.fixture(scope="function") 
    def home_page(self, driver):
        """Create HomePage instance"""
        return HomePage(driver)
    
    def test_homepage_loads_successfully(self, home_page):
        """
        Test that Amazon India homepage loads correctly
        Demonstrates basic navigation with AI-enhanced elements
        """
        # Navigate to homepage
        assert home_page.navigate_to_home(), "Failed to load Amazon India homepage"
        
        # Verify page title contains Amazon
        title = home_page.get_page_title()
        assert "Amazon" in title, f"Unexpected page title: {title}"
        
        # Verify key elements are present using AI-enhanced locators
        search_bar = home_page.find_element_ai("search_bar")
        assert search_bar is not None, "Search bar not found with AI assistance"
        
        cart_button = home_page.find_element_ai("cart_button")
        assert cart_button is not None, "Cart button not found with AI assistance"
    
    @pytest.mark.smoke
    def test_product_search_functionality(self, home_page):
        """
        Test product search with AI-enhanced element detection
        Demonstrates self-healing locators in action
        """
        # Navigate to homepage
        home_page.navigate_to_home()
        
        # Search for a popular product in India
        search_term = "iPhone 15"
        success = home_page.search_for_product(search_term)
        assert success, f"Failed to search for '{search_term}'"
        
        # Verify we're on search results page
        current_url = home_page.driver.current_url
        assert "s?" in current_url or "search" in current_url, "Not redirected to search results"
        
        # Verify search term appears in page title or URL
        title = home_page.get_page_title()
        assert search_term.lower() in title.lower() or search_term.lower() in current_url.lower(), \
            f"Search term '{search_term}' not found in title or URL"
    
    @pytest.mark.critical
    def test_location_selector_functionality(self, home_page):
        """
        Test location selection for delivery
        Demonstrates AI-powered element interaction
        """
        home_page.navigate_to_home()
        
        # Test location selector
        success = home_page.select_location("Mumbai")
        assert success, "Failed to interact with location selector"
    
    def test_cart_functionality(self, home_page):
        """Test shopping cart basic functionality"""
        home_page.navigate_to_home()
        
        # Get initial cart count (should be 0 for new session)
        initial_count = home_page.get_cart_count()
        assert initial_count >= 0, "Invalid cart count"
        
        # Verify cart button is clickable
        cart_button = home_page.find_element_ai("cart_button")
        assert cart_button is not None, "Cart button not accessible"
        assert cart_button.is_enabled(), "Cart button not enabled"
    
    @pytest.mark.visual
    def test_homepage_visual_elements(self, home_page):
        """
        Test visual elements are properly loaded
        Demonstrates AI visual testing capabilities when enabled
        """
        home_page.navigate_to_home()
        
        # Check if Prime member section is visible (common in Amazon India)
        prime_visible = home_page.is_prime_member_section_visible()
        # Note: This might be True or False depending on user session
        assert isinstance(prime_visible, bool), "Prime visibility check failed"
        
        # Verify key navigation elements are visible
        elements_to_check = ["search_bar", "cart_button", "account_menu"]
        
        for element_name in elements_to_check:
            element = home_page.find_element_ai(element_name)
            assert element is not None, f"Critical element '{element_name}' not found"
            assert element.is_displayed(), f"Element '{element_name}' not visible"
    
    @pytest.mark.performance
    def test_page_load_performance(self, home_page):
        """Test homepage loads within acceptable time"""
        import time
        
        start_time = time.time()
        success = home_page.navigate_to_home()  
        load_time = time.time() - start_time
        
        assert success, "Homepage failed to load"
        assert load_time < 10, f"Homepage took too long to load: {load_time:.2f}s"
        
    @pytest.mark.accessibility  
    def test_basic_accessibility(self, home_page):
        """Basic accessibility checks"""
        home_page.navigate_to_home()
        
        # Check that search bar has proper attributes
        search_bar = home_page.find_element_ai("search_bar")
        assert search_bar is not None, "Search bar not found"
        
        # Verify essential attributes exist
        placeholder = search_bar.get_attribute("placeholder")
        assert placeholder is not None, "Search bar missing placeholder text"
        
        # Check cart has aria-label or title for screen readers
        cart_button = home_page.find_element_ai("cart_button")
        if cart_button:
            aria_label = cart_button.get_attribute("aria-label")
            title = cart_button.get_attribute("title")
            assert aria_label or title, "Cart button missing accessibility attributes"


# Additional test configuration
pytestmark = [
    pytest.mark.amazon,
    pytest.mark.e_commerce,
    pytest.mark.india
]
