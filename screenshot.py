import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Create screenshots directory
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

try:
    # List of pages to capture
    pages = [
        {"url": "http://localhost:5000/dashboard/", "file": "dashboard"},
        {"url": "http://localhost:5000/vc-lens/", "file": "vc_lens"},
        {"url": "http://localhost:5000/copilot/", "file": "copilot"},
        {"url": "http://localhost:5000/strategy-hub/", "file": "strategy_hub"}
    ]
    
    # Capture each page
    for page in pages:
        print(f"Capturing {page['file']}...")
        driver.get(page["url"])
        time.sleep(2)  # Wait for page to fully load
        driver.save_screenshot(f"screenshots/{page['file']}.png")
        print(f"Saved screenshot of {page['file']}")
        
    print("All screenshots captured successfully!")
        
except Exception as e:
    print(f"Error capturing screenshots: {str(e)}")
finally:
    driver.quit()