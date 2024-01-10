import os
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def extract_info_from_url(url):
    if not is_valid_asos_product_link(url):
        print("Not a valid ASOS link")
        return
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_argument("--enable-logging")  # Enable browser logging
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    path = os.getenv('CHROMEDRIVER_PATH')

    driver = webdriver.Chrome(path, options=options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the name element to be present on the page
        name_element = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "jcdpl"))
        )

        # Extract the name text
        name_text = name_element.get_attribute("innerText").strip()
        print("Product Name:", name_text)

        try:
            price_element = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//span[@data-testid='current-price' and contains(@class, 'MwTOW BR6YF')]")
                )
            )
        except TimeoutException:
            # If the first attempt times out, try the second XPATH without 'BR6YF'
            price_element = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//span[@data-testid='current-price' and contains(@class, 'MwTOW')]")
                )
            )

        # Extract the price text
        price_text = price_element.get_attribute("innerText").strip()

        # Split the price_text into parts
        parts = price_text.split()

        if len(parts) == 3 and parts[0] == "Now":
            # Extract the price_number and price_currency
            price_number = float(parts[1])
            price_currency = parts[2]

            print("Price Number:", price_number)
            print("Price Currency:", price_currency)

        elif len(parts) == 2 and parts[0] != "Now":
            # Extract the price_number and price_currency
            price_number = float(parts[0])
            price_currency = parts[1]

            print("Price Number:", price_number)
            print("Price Currency:", price_currency)

        else:
            print("Unexpected price format.")

            # Return the extracted values
        return price_currency, name_text, price_number

    except TimeoutException as te:
        print(f"TimeoutException: {te}")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver
        driver.quit()


def is_valid_asos_product_link(link):
    # Regular expression to match ASOS product links
    asos_link_pattern = re.compile(r'https://www\.asos\.com/.+/prd/\d+.*')

    # Check if the link matches the pattern
    return bool(asos_link_pattern.match(link))