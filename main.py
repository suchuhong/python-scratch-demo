"""
Basic example of web automation using Selenium
This script:
1. Opens a browser
2. Navigates to Wikipedia
3. Searches for a term
4. Extracts data from the page
5. Demonstrates various Selenium features
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Import our utility functions
from utils import (
    setup_chrome_driver,
    wait_for_element,
    safe_click,
    fill_form_field,
    take_screenshot,
    get_element_text
)


def search_wikipedia(driver, search_term):
    """Search Wikipedia for a term and return the first paragraph text"""
    # Navigate to Wikipedia
    driver.get("https://en.wikipedia.org/")
    
    # Find the search input box
    search_input = wait_for_element(
        driver, 
        (By.ID, "searchInput"), 
        condition="visibility"
    )
    
    # Enter search term and submit
    search_input.clear()
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    
    # Wait for the page to load
    wait_for_element(
        driver, 
        (By.ID, "firstHeading"), 
        condition="visibility"
    )
    
    # Take a screenshot
    take_screenshot(driver, f"wikipedia_{search_term}")
    
    # Get the first paragraph
    first_paragraph_locator = (By.CSS_SELECTOR, ".mw-parser-output > p:not(.mw-empty-elt)")
    first_paragraph = get_element_text(driver, first_paragraph_locator)
    
    return first_paragraph


def main():
    # Initialize the WebDriver
    print("Initializing Chrome WebDriver...")
    driver = setup_chrome_driver(headless=False)
    
    try:
        # Set implicit wait for the entire session
        driver.implicitly_wait(10)
        
        # Search Wikipedia and get results
        search_term = "Python programming language"
        print(f"Searching Wikipedia for: {search_term}")
        
        first_paragraph = search_wikipedia(driver, search_term)
        
        # Display results
        print("\n--- Search Results ---")
        print(f"First paragraph: {first_paragraph[:300]}...")
        
        # Demonstrate additional features
        print("\nDemonstrating browser navigation...")
        
        # Go back to the Wikipedia home page
        driver.back()
        time.sleep(1)
        
        # Go forward again
        driver.forward()
        time.sleep(1)
        
        # Refresh the page
        driver.refresh()
        time.sleep(1)
        
        print("Automation completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        take_screenshot(driver, "error_screenshot")
    
    finally:
        # Always close the browser to free resources
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main() 