from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

print("Starting Selenium script...")

try:
    # Set Chrome options for headless execution
    chrome_options = Options()

    # Get options from environment variable set in Dockerfile
    # This allows easy modification of Chrome flags without rebuilding Dockerfile
    chrome_flags = os.getenv("CHROME_OPTIONS", "--no-sandbox --headless --disable-gpu --disable-dev-shm-usage")
    for flag in chrome_flags.split():
        chrome_options.add_argument(flag)

    # Initialize the Chrome driver using webdriver_manager
    # It will automatically download the correct ChromeDriver version
    # and ensure it's compatible with the installed Chrome browser.
    print("Initializing ChromeDriver...")
    service = Service(ChromeDriverManager().install())

    # Create a new Chrome browser instance
    print("Creating Chrome browser instance...")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to a website
    url = "https://www.google.com"
    print(f"Navigating to {url}...")
    driver.get(url)

    # Print the page title
    page_title = driver.title
    print(f"Page title: {page_title}")

    # You can add more Selenium actions here
    # For example, taking a screenshot:
    # driver.save_screenshot("google_homepage.png")
    # print("Screenshot saved as google_homepage.png")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Always quit the driver to close the browser and free resources
    if 'driver' in locals() and driver:
        print("Quitting WebDriver...")
        driver.quit()
    print("Selenium script finished.")