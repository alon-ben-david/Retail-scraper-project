from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Headless mode
options = Options()
options.headless = True
options.add_argument('window-size=1920x1080')
options.add_argument("--enable-logging")  # Enable browser logging
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

path = '/Users/alonbendavid/PycharmProjects/Web Scraping Course/Introduction to Selenium/chromedriver_mac_arm64/chromedriver'

url = "https://www.asos.com/tommy-hilfiger/tommy-hilfiger-logo-tipped-crew-neck-sweatshirt-in-black/prd/205438664#colourWayId-205438665"

driver = webdriver.Chrome(path, options=options)

# Navigate to the URL
driver.get(url)

try:

    # Wait for the name element to be present on the page
    name_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "jcdpl"))
    )


    # Extract the name text
    name_text = name_element.get_attribute("innerText").strip()
    print("Product Name:", name_text)

    # Wait for the price element to be present on the page
    price_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'ky6t2')]"))
    )


    # Extract the price text
    price_text = price_element.get_attribute("innerText").strip()
    print("Product Price:", price_text)

except TimeoutException as te:
    print(f"TimeoutException: {te}")
except Exception as e:
    print(f"An error occurred: {e}")

finally:

    # Close the WebDriver
    driver.quit()
