"""
Example: Handling dynamic content and AJAX with Selenium
This script demonstrates how to:
1. Interact with dynamic content that loads via JavaScript
2. Handle infinite scrolling pages
3. Wait for AJAX requests to complete
"""
import time
import os
import sys
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    setup_chrome_driver,
    wait_for_element,
    safe_click,
    get_element_text
)


def wait_for_ajax(driver, timeout=10):
    """
    Wait for all AJAX requests to complete
    
    Args:
        driver: WebDriver instance
        timeout: Maximum time to wait in seconds
    """
    # JavaScript to check if jQuery is active and if there are pending AJAX requests
    script = """
    return (typeof jQuery !== 'undefined') ? 
        jQuery.active === 0 : true;
    """
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(script)
    )


def scroll_to_bottom(driver):
    """
    Scroll to the bottom of the page
    
    Args:
        driver: WebDriver instance
    """
    # Get current scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(2)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same, no more content to load
            break
        last_height = new_height


def collect_lazy_loaded_items(driver, max_items=50) -> List[str]:
    """
    Collect items from a dynamically loaded page with infinite scroll
    
    Args:
        driver: WebDriver instance
        max_items: Maximum number of items to collect
        
    Returns:
        List of item texts
    """
    # Navigate to a page with infinite scroll
    driver.get("https://infinite-scroll.com/demo/full-page/")
    
    # Wait for initial items to load
    wait_for_element(
        driver,
        (By.CSS_SELECTOR, ".article-item"),
        condition="presence",
        timeout=10
    )
    
    items = []
    last_count = 0
    
    # Keep scrolling until we have enough items or no new items are loading
    while len(items) < max_items:
        # Get current items
        article_elements = driver.find_elements(By.CSS_SELECTOR, ".article-item")
        
        # Extract text from new items
        for i in range(last_count, len(article_elements)):
            if i < len(article_elements):
                title_element = article_elements[i].find_element(By.CSS_SELECTOR, "h2")
                items.append(title_element.text)
                print(f"Found item: {title_element.text}")
        
        # Check if we've collected enough items
        if len(items) >= max_items:
            break
        
        # Record current count
        last_count = len(article_elements)
        
        # Scroll down to load more items
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        
        # Wait for new items to load
        try:
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".article-item")) > last_count
            )
        except TimeoutException:
            # No new items loaded, we've reached the end or there's a loading issue
            print("No more items loading, or reached the end of content")
            break
    
    return items[:max_items]


def handle_modal_dialogs(driver):
    """
    Demonstrate handling modal dialogs and popups
    
    Args:
        driver: WebDriver instance
    """
    # Navigate to a page with modals
    driver.get("https://getbootstrap.com/docs/4.0/components/modal/")
    
    # Find and click the button to launch a modal
    launch_button = wait_for_element(
        driver,
        (By.CSS_SELECTOR, "[data-target='#exampleModal']"),
        condition="clickable"
    )
    safe_click(driver, launch_button)
    
    # Wait for the modal to appear
    modal = wait_for_element(
        driver,
        (By.ID, "exampleModal"),
        condition="visibility"
    )
    
    # Get text from the modal
    modal_title = get_element_text(
        driver, 
        (By.CSS_SELECTOR, "#exampleModal .modal-title")
    )
    modal_body = get_element_text(
        driver,
        (By.CSS_SELECTOR, "#exampleModal .modal-body")
    )
    
    print(f"Modal Title: {modal_title}")
    print(f"Modal Body: {modal_body}")
    
    # Close the modal
    close_button = modal.find_element(By.CSS_SELECTOR, "button.close")
    safe_click(driver, close_button)
    
    # Wait for modal to disappear
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "exampleModal"))
    )


def main():
    print("Starting Selenium demo for dynamic content...")
    driver = setup_chrome_driver(headless=False)
    
    try:
        # Part 1: Collect items from infinite scroll page
        print("\n=== Infinite Scroll Demo ===")
        items = collect_lazy_loaded_items(driver, max_items=10)
        print(f"Collected {len(items)} items from infinite scroll:")
        for i, item in enumerate(items[:5], 1):
            print(f"{i}. {item}")
        
        # Part 2: Handle modal dialogs
        print("\n=== Modal Dialog Demo ===")
        handle_modal_dialogs(driver)
        
    except Exception as e:
        print(f"Error occurred: {e}")
    
    finally:
        # Always close the browser
        driver.quit()


if __name__ == "__main__":
    main() 