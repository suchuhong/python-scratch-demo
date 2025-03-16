"""
Utility functions for Selenium web automation
"""
import time
from typing import Tuple, Any, List, Optional

from selenium import webdriver
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def setup_chrome_driver(headless: bool = False, disable_images: bool = False) -> Chrome:
    """
    Set up Chrome WebDriver with optional configurations
    
    Args:
        headless: Run browser in headless mode (no UI)
        disable_images: Disable image loading for faster browsing
        
    Returns:
        Configured Chrome WebDriver instance
    """
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    service = ChromeService(ChromeDriverManager().install())
    driver = Chrome(service=service, options=options)
    return driver


def setup_firefox_driver(headless: bool = False) -> Firefox:
    """
    Set up Firefox WebDriver with optional configurations
    
    Args:
        headless: Run browser in headless mode (no UI)
        
    Returns:
        Configured Firefox WebDriver instance
    """
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = Firefox(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver


def wait_for_element(
    driver: WebDriver, 
    locator: Tuple[By, str], 
    timeout: int = 10, 
    condition: str = "presence"
) -> WebElement:
    """
    Wait for an element to be present/visible/clickable
    
    Args:
        driver: WebDriver instance
        locator: Tuple of By strategy and locator string
        timeout: Maximum time to wait in seconds
        condition: One of 'presence', 'visibility', or 'clickable'
        
    Returns:
        WebElement when found
        
    Raises:
        TimeoutException: If element is not found within timeout
    """
    wait = WebDriverWait(driver, timeout)
    
    if condition == "presence":
        return wait.until(EC.presence_of_element_located(locator))
    elif condition == "visibility":
        return wait.until(EC.visibility_of_element_located(locator))
    elif condition == "clickable":
        return wait.until(EC.element_to_be_clickable(locator))
    else:
        raise ValueError(f"Invalid condition: {condition}")


def safe_click(driver: WebDriver, element: WebElement, retries: int = 3) -> bool:
    """
    Safely click an element with retries and error handling
    
    Args:
        driver: WebDriver instance
        element: WebElement to click
        retries: Number of retry attempts
        
    Returns:
        True if click was successful, False otherwise
    """
    for attempt in range(retries):
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)  # Small delay after scrolling
            element.click()
            return True
        except (ElementNotInteractableException, StaleElementReferenceException) as e:
            if attempt == retries - 1:
                print(f"Failed to click element after {retries} attempts: {e}")
                return False
            time.sleep(1)  # Wait before retrying
    
    return False


def fill_form_field(
    driver: WebDriver, 
    locator: Tuple[By, str], 
    text: str, 
    clear_first: bool = True
) -> bool:
    """
    Fill a form field with text
    
    Args:
        driver: WebDriver instance
        locator: Tuple of By strategy and locator string
        text: Text to enter in the field
        clear_first: Whether to clear the field before entering text
        
    Returns:
        True if operation was successful, False otherwise
    """
    try:
        element = wait_for_element(driver, locator, condition="visibility")
        if clear_first:
            element.clear()
        element.send_keys(text)
        return True
    except (TimeoutException, ElementNotInteractableException) as e:
        print(f"Failed to fill form field: {e}")
        return False


def take_screenshot(driver: WebDriver, filename: str) -> str:
    """
    Take a screenshot and save it
    
    Args:
        driver: WebDriver instance
        filename: Name of the file to save (without extension)
        
    Returns:
        Path to the saved screenshot
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = f"{filename}_{timestamp}.png"
    driver.save_screenshot(filepath)
    return filepath


def get_element_text(driver: WebDriver, locator: Tuple[By, str], timeout: int = 10) -> Optional[str]:
    """
    Get text from an element
    
    Args:
        driver: WebDriver instance
        locator: Tuple of By strategy and locator string
        timeout: Maximum time to wait in seconds
        
    Returns:
        Element text or None if element not found
    """
    try:
        element = wait_for_element(driver, locator, timeout=timeout, condition="visibility")
        return element.text
    except TimeoutException:
        return None 