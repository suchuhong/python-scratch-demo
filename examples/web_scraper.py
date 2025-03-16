"""
Advanced example: Web scraping with Selenium
This script demonstrates how to scrape product information from a demo e-commerce site
"""
import time
import csv
import os
from typing import List, Dict, Any
from selenium.webdriver.common.by import By

# Import from parent directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    setup_chrome_driver,
    wait_for_element,
    safe_click,
    get_element_text
)


def scrape_products(url: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """
    Scrape product information from a demo e-commerce site
    
    Args:
        url: URL of the e-commerce site
        max_pages: Maximum number of pages to scrape
        
    Returns:
        List of product dictionaries with name, price, and description
    """
    # Initialize Chrome driver (headless for faster scraping)
    driver = setup_chrome_driver(headless=True, disable_images=True)
    products = []
    
    try:
        # Navigate to the e-commerce site
        driver.get(url)
        
        # Process each page up to max_pages
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page} of {max_pages}...")
            
            # Wait for products to load
            product_elements = wait_for_element(
                driver,
                (By.CSS_SELECTOR, ".product-item"),
                condition="presence"
            ).find_elements(By.XPATH, "./parent::*/*")  # Get all product items
            
            # Extract product information
            for product_element in product_elements:
                try:
                    # Get product name
                    name_element = product_element.find_element(By.CSS_SELECTOR, ".product-name")
                    name = name_element.text
                    
                    # Get product price
                    price_element = product_element.find_element(By.CSS_SELECTOR, ".product-price")
                    price = price_element.text
                    
                    # Click on product to get more details
                    safe_click(driver, name_element)
                    
                    # Wait for product description to load
                    description = get_element_text(
                        driver,
                        (By.CSS_SELECTOR, ".product-description"),
                        timeout=5
                    )
                    
                    # Add product to list
                    products.append({
                        "name": name,
                        "price": price,
                        "description": description if description else "No description available"
                    })
                    
                    # Go back to product list
                    driver.back()
                    time.sleep(1)  # Small delay to let the page load
                    
                except Exception as e:
                    print(f"Error scraping product: {e}")
                    continue
            
            # Check if there's a next page button and click it
            if page < max_pages:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".pagination .next")
                    if next_button.is_enabled():
                        safe_click(driver, next_button)
                        time.sleep(2)  # Wait for the new page to load
                    else:
                        print("No more pages available")
                        break
                except Exception:
                    print("No more pages available")
                    break
    
    finally:
        # Always close the browser
        driver.quit()
    
    return products


def save_to_csv(products: List[Dict[str, Any]], filename: str = "products.csv") -> None:
    """
    Save product data to a CSV file
    
    Args:
        products: List of product dictionaries
        filename: Name of the CSV file to save
    """
    # Ensure we have data to save
    if not products:
        print("No products to save")
        return
    
    # Get fieldnames from the first product
    fieldnames = products[0].keys()
    
    # Write data to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    
    print(f"Saved {len(products)} products to {filename}")


def main():
    # Demo e-commerce site URL
    url = "https://webscraper.io/test-sites/e-commerce/allinone"
    
    print("Starting web scraping with Selenium...")
    products = scrape_products(url, max_pages=2)
    
    print(f"Scraped {len(products)} products")
    
    # Display the first few products
    for i, product in enumerate(products[:3], 1):
        print(f"\nProduct {i}:")
        print(f"  Name: {product['name']}")
        print(f"  Price: {product['price']}")
        print(f"  Description: {product['description'][:100]}...")
    
    # Save data to CSV
    save_to_csv(products)


if __name__ == "__main__":
    main() 