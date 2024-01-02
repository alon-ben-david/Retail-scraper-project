from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.options import Options
import pandas as pd


website = 'https://www.adamchoi.co.uk/overs/detailed'

path = '/Users/alonbendavid/PycharmProjects/Web Scraping Course/Introduction to Selenium/chromedriver_mac_arm64/chromedriver'
url = 'https://www.asos.com/topman/topman-oversized-collarless-jersey-blazer-in-grey/prd/202285673#colourWayId-202285676?ctaref=recently%20viewed'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
service = Service(path)
driver = webdriver.Chrome(path)
# Navigate to the website
#driver.get(website)


# Open the URL
driver.get(url)
try:
    # Locate the span element using its class
    price_element = driver.find_element(By.CLASS_NAME, 'MwTOW')

    # Extract the text content of the span
    price_text = price_element.text
# Use regular expressions to extract price and currency
    match = re.match(r'Now (\d+\.\d+) (\w+)', price_text)

    if match:
        price = match.group(1)
        currency = match.group(2)

        print('Price:', price)
        print('Currency:', currency)
    else:
        print('Pattern not matched. Check the element class or structure.')

finally:
    # Close the browser window
    driver.quit()