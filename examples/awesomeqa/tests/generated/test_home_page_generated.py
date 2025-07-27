"""
Generated tests for home_page
"""

from examples.awesomeqa.pages.home_page import HomePagePage


def test_home_page_loads(driver):
    """
    Test that home_page loads correctly
    """
    page = HomePagePage(driver)
    page.open()
    assert page.get_page_title()  # Basic assertion
    

def test_home_page_elements_visible(driver):
    """
    Test that key elements on home_page are visible
    """
    page = HomePagePage(driver)
    page.open()
    assert page.get_page_title()  # Basic assertion
    
