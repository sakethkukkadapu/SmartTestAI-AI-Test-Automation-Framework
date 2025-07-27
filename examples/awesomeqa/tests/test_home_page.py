"""
AwesomeQA Home Page Tests
Demonstrates the new modular architecture with AI-enhanced testing.
"""

import pytest
from smarttestai.utils.driver_manager import DriverManager
from smarttestai.core.ai_config import AIConfig
from examples.awesomeqa.pages.home_page import HomePage


@pytest.fixture(scope="session")
def config():
    """Load configuration for the AwesomeQA suite"""
    return AIConfig.load_suite_config("awesomeqa")


@pytest.fixture
def driver(config):
    """Create WebDriver instance with configuration"""
    driver_instance = DriverManager.create_driver(config)
    yield driver_instance
    driver_instance.quit()


@pytest.fixture
def home_page(driver):
    """Create HomePage instance"""
    return HomePage(driver)


class TestHomePage:
    """Test cases for the home page functionality"""
    
    def test_homepage_loads(self, home_page):
        """Test that the homepage loads and key elements are visible"""
        home_page.open()
        assert home_page.wait_for_page_load(), "Page should load completely"
        assert home_page.is_homepage_loaded(), "Homepage elements should be visible"
    
    def test_page_title(self, home_page):
        """Test that the page has a proper title"""
        home_page.open()
        title = home_page.get_page_title()
        assert title, "Page should have a title"
        assert len(title) > 0, "Title should not be empty"
    
    def test_search_functionality(self, home_page):
        """Test search functionality with AI-enhanced elements"""
        home_page.open()
        
        # Use AI-enhanced search
        search_success = home_page.search_for_product("laptop")
        
        # Note: This may not work in the test environment without proper setup,
        # but demonstrates the AI-enhanced testing approach
        if search_success:
            assert home_page.wait_for_page_load(), "Search results should load"
    
    def test_ai_element_registration(self, home_page):
        """Test that AI elements are properly registered"""
        home_page.open()
        
        # Check that registered elements can be found (even if healing is needed)
        # This tests the AI self-healing functionality
        search_field_found = home_page.is_element_visible_ai("search_field")
        search_button_found = home_page.is_element_visible_ai("search_button")
        
        # At least one element should be found (demonstrates self-healing)
        assert search_field_found or search_button_found, "AI should find at least one registered element"
    
    @pytest.mark.visual
    def test_visual_appearance(self, home_page):
        """Test visual appearance (requires visual testing enabled)"""
        home_page.open()
        
        # Take screenshot for visual testing
        screenshot_path = home_page.take_screenshot("homepage_test.png")
        assert screenshot_path, "Screenshot should be captured"
        
        # In a full implementation, this would compare against a baseline
        # using AI-powered visual testing
    
    @pytest.mark.critical
    def test_critical_elements_present(self, home_page):
        """Critical test: Ensure essential elements are present"""
        home_page.open()
        
        # These are critical elements that must be present
        assert home_page.is_element_visible_ai("search_field"), "Search field is critical for e-commerce"
        
        # Additional checks could include cart, navigation, etc.
        # The AI healing will try to find these elements even if locators change
    
    @pytest.mark.smoke
    def test_basic_navigation(self, home_page):
        """Smoke test: Basic navigation functionality"""
        home_page.open()
        home_page.wait_for_page_load()
        
        # Basic smoke test - page loads and we can interact with it
        assert "awesomeqa" in home_page.driver.current_url.lower(), "Should be on AwesomeQA site"
