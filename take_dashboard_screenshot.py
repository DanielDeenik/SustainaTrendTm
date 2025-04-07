"""
Take a screenshot of the running dashboard application.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def take_screenshot(url, output_file):
    """
    Take a screenshot of the specified URL using headless Chrome
    """
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for page to load completely
        time.sleep(3)
        
        # Take screenshot
        print(f"Taking screenshot and saving to {output_file}...")
        driver.save_screenshot(output_file)
        print(f"Screenshot saved to {output_file}")
        
        # Close the driver
        driver.quit()
        return True
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return False

if __name__ == "__main__":
    # Take screenshots of different pages
    urls = [
        "http://localhost:5000/dashboard/",
        "http://localhost:5000/vc-lens/",
        "http://localhost:5000/copilot/"
    ]
    for i, url in enumerate(urls):
        take_screenshot(url, f"screenshot_{i+1}.png")