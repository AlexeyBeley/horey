from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

v_display = Display(visible=0, size=(1920, 1080))
v_display.start()
options = Options()
options.binary_location = "/usr/bin/chromium"  # Explicitly use Chromium
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Point to the driver installed by apt
service = Service(executable_path="/usr/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://google.com")
print(driver.title)
driver.quit()