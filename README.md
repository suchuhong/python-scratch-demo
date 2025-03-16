# Python + Selenium Web Automation

This project demonstrates how to use Selenium with Python for web automation tasks.

[中文文档](README_zh.md) | [English](README.md)

**Documentation:**
- [Advanced Usage Guide (Chinese)](advanced_guide_zh.md) - Solutions for complex scenarios

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. WebDriver Setup:
   - For Chrome: The project uses webdriver-manager which will automatically download and manage the appropriate ChromeDriver version
   - For other browsers: You'll need to download the appropriate driver and update the scripts accordingly

## Project Structure

- `main.py`: Basic example of Selenium automation
- `utils.py`: Helper functions for common Selenium operations
- `examples/`: Additional example scripts for different use cases

## Usage

Run the basic example:
```
python main.py
```

## Common Tasks

The following examples show how to perform common tasks with Selenium:

### Navigate to a URL
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.example.com")
```

### Find elements
```python
# Find by ID
element = driver.find_element(By.ID, "search")

# Find by CSS Selector
element = driver.find_element(By.CSS_SELECTOR, "button.submit")

# Find by XPath
element = driver.find_element(By.XPATH, "//button[@type='submit']")
```

### Interact with elements
```python
# Click a button
button = driver.find_element(By.ID, "submit-button")
button.click()

# Input text
input_field = driver.find_element(By.NAME, "username")
input_field.send_keys("my_username")

# Clear input field
input_field.clear()
```

### Wait for elements
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for element to be clickable (explicit wait)
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "submit-button"))
)
element.click()
``` 