from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv
import os

load_dotenv()

firefox_path = os.getenv("FIREFOX")
driver_path = os.getenv("GECKODRIVER")

options = Options()
options.binary_location = str(firefox_path)
options.add_argument("--headless")

service = Service(executable_path=str(driver_path))

driver = webdriver.Firefox(service=service, options=options)
driver.get("https://www.google.com")
print(driver.title)

driver.quit()
