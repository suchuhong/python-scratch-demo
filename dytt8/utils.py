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
# 尝试导入webdriver_manager，但不再将其作为必需依赖
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True

    # 尝试从不同的位置导入ChromeType，适应不同版本的webdriver_manager
    try:
        # 较新版本的webdriver_manager
        from webdriver_manager.core.utils import ChromeType
    except ImportError:
        try:
            # 较旧版本的webdriver_manager
            from webdriver_manager.utils import ChromeType
        except ImportError:
            # 如果无法导入，创建一个简单的枚举类替代
            class ChromeType:
                GOOGLE = "GOOGLE"
                CHROMIUM = "CHROMIUM"
                MSEDGE = "MSEDGE"
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("webdriver_manager 未安装，将使用 Selenium 自动驱动管理")


def setup_chrome_driver(headless: bool = False, disable_images: bool = False) -> Chrome:
    """
    Set up Chrome WebDriver with optional configurations
    使用 Selenium 4 自动驱动管理功能，不再依赖 webdriver_manager
    
    Args:
        headless: Run browser in headless mode (no UI)
        disable_images: Disable image loading for faster browsing
        
    Returns:
        Configured Chrome WebDriver instance
    """
    print("设置 Chrome WebDriver...")
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # 新版Chrome使用的headless参数
        options.add_argument("--disable-gpu")
    
    # 基本设置
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")  # 解决跨域问题
    
    # 禁用webdriver特征标识，避免被网站检测
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    # 方法1：直接使用 Selenium 4 的自动驱动管理（推荐）
    try:
        print("使用 Selenium 4 自动驱动管理功能...")
        driver = Chrome(options=options)
        print("成功创建 Chrome WebDriver 实例")
        return driver
    except Exception as e:
        print(f"使用自动驱动管理创建 WebDriver 失败: {e}")
        
        # 方法2：如果 webdriver_manager 可用，尝试使用它
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                print("尝试使用 webdriver_manager...")
                # 尝试各种安装方法
                try:
                    service = ChromeService(ChromeDriverManager().install())
                except Exception as e2:
                    print(f"标准安装方法失败: {e2}")
                    try:
                        service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
                    except Exception:
                        print("所有 webdriver_manager 方法都失败，使用基本 Service")
                        service = ChromeService()
                
                driver = Chrome(service=service, options=options)
                print("使用 webdriver_manager 成功创建 WebDriver")
                return driver
            except Exception as e3:
                print(f"所有方法都失败: {e3}")
                raise
        else:
            # 如果 webdriver_manager 不可用，重新尝试基本方法
            print("再次尝试直接创建 WebDriver...")
            try:
                service = ChromeService()
                driver = Chrome(service=service, options=options)
                print("成功创建 Chrome WebDriver 实例")
                return driver
            except Exception as e4:
                print(f"所有创建 WebDriver 方法都失败: {e4}")
                raise


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
    
    # 直接使用 Selenium 4 自动驱动管理
    try:
        driver = Firefox(options=options)
        driver.set_window_size(1920, 1080)
        return driver
    except Exception as e:
        print(f"使用 Selenium 自动驱动管理创建 Firefox WebDriver 失败: {e}")
        
        # 尝试使用 webdriver_manager
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = FirefoxService(GeckoDriverManager().install())
                driver = Firefox(service=service, options=options)
                driver.set_window_size(1920, 1080)
                return driver
            except Exception as e2:
                print(f"使用 webdriver_manager 创建 Firefox WebDriver 失败: {e2}")
                raise
        else:
            raise


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