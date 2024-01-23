import os
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import time
from currency_converter import convert_currency
import concurrent.futures  # For threading
import traceback


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


def extract_asos_product_id(url):
    # Regular expression to extract the product ID from ASOS URLs
    pattern = re.compile(r'/prd/(\d+)')

    # Search for the pattern in the URL
    match = pattern.search(url)

    # Check if a match is found and return the product ID
    if match:
        return match.group(1)
    else:
        return None


def build_request_link(product_id):
    base_url = "https://codembo.com/en/prd/"
    currency_param = "?cur=EUR"
    return base_url + str(product_id) + currency_param


def extract_info_codembo_url(url):
    try:
        time.sleep(2)

        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        print(traceback.format_exc())
        return None, None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        product_name_element = soup.select_one('h1.prd-card-title')

        if product_name_element:
            product_name = product_name_element.text.strip()
        else:
            print("Product name not found.")
            return None, None

        product_prices = {}

        for row in soup.select('table.goodt tbody tr'):
            country_code_element = row.select_one('td')
            price_element = row.select_one('td:nth-of-type(2)')

            if country_code_element and price_element:
                country_code = country_code_element.text.strip()
                price = price_element.text.strip()
                product_prices[country_code] = price

        return product_name, product_prices

    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None, None


def create_dataframe(products):
    data = []
    for product_name, product_prices in products:
        product_data = {'product_name': product_name}

        product_data.update(product_prices)

        for country_code in product_prices.keys():
            availability_column_name = f'{country_code}_available'

            for country_code in product_prices.keys():
                availability_column_name = f'{country_code}_available'
                product_data[availability_column_name] = not pd.isnull(product_prices[country_code])
        # Append the product data to the list
        data.append(product_data)

    df = pd.DataFrame(data)

    print(df.columns)
    df = df.fillna(False)
    sum_df = pd.DataFrame(index=['Sum'])
    for country_code in product_prices.keys():
        df[country_code] = pd.to_numeric(df[country_code],
                                         errors='coerce')
        sum_df[country_code] = df[country_code].sum().round(2)
    can_use_il17(df, sum_df)
    export_to_csv(sum_df, 'sum_output.csv')
    export_to_csv(df)

    return df, sum_df


def analyze_price_each_country(df, sum_df):
    sorted_sum = sum_df.unstack().sort_values()

    smallest_values = sorted_sum.head(2)
    cheapest_country, second_cheapest_country = [col[0] for col in smallest_values.index]
    print(cheapest_country)
    print(second_cheapest_country)
    result_df, sum_basket = compare_prices(df, cheapest_country, second_cheapest_country)
    result_df = result_df.reset_index(drop=True)
    split_and_print_basket(result_df)
    basket_dict = {}

    for index, row in result_df.iterrows():
        product_name = row['product_name']
        country = row['Country']
        price = row['Cheapest_Price']

        if country not in basket_dict:
            basket_dict[country] = {'products': [], 'total_price': 0}

        basket_dict[country]['products'].append({'product_name': product_name, 'price': price})
        basket_dict[country]['total_price'] += price

    for country, details in basket_dict.items():
        print(f"Country: {country}")
        print("Products:")
        for product in details['products']:
            print(f"  - {product['product_name']}: {product['price']}")
        print(f"Total Price: {details['total_price']:.2f}")

    return result_df


def compare_prices(df, cheapest_country, second_cheapest_country):
    result_list = []

    for index, row in df.iterrows():
        product_name = row['product_name']

        if row[cheapest_country] == 0.0 and row[second_cheapest_country] == 0.0:
            non_zero_prices = {col: price for col, price in row.items() if price != 0}
            if non_zero_prices:
                cheapest_country = min(non_zero_prices, key=non_zero_prices.get)
                cheapest_price = non_zero_prices[cheapest_country]
            else:
                cheapest_country = None
                cheapest_price = 0.0
        else:
            cheapest_price = row[cheapest_country] if row[second_cheapest_country] == 0.0 else (
                row[second_cheapest_country] if row[cheapest_country] == 0.0 else min(row[cheapest_country],
                                                                                      row[second_cheapest_country])
            )

        country = cheapest_country if row[cheapest_country] == cheapest_price else second_cheapest_country

        result_list.append({'product_name': product_name, 'Country': country, 'Cheapest_Price': cheapest_price})

    result_df = pd.DataFrame(result_list)

    sum_basket = result_df['Cheapest_Price'].sum()
    print(f"Total cost of the basket in the cheapest country:{sum_basket:.2f}")
    print(result_df)
    export_to_csv(result_df, 'result_df_output.csv')

    return result_df, sum_basket


def export_to_csv(df, filename='product_prices.csv'):
    df.to_csv(filename, index=False)
    print(f'DataFrame exported to {filename}')


def extract_product_id_from_url(url):
    data = {
        'Name': [],
        'Image Link': [],
        'Id': [],
        'Link': []
    }
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_argument("--enable-logging")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    path = os.getenv('CHROMEDRIVER_PATH')

    driver = webdriver.Chrome(path, options=options)

    try:
        driver.get(url)

        container_element = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "productTilesWrapper_LkXSW"))
        )

        soup = BeautifulSoup(container_element.get_attribute("outerHTML"), 'html.parser')

        li_elements = soup.find_all('li')

        for li in li_elements:
            time.sleep(2)
            print(li)
            if li.find('a') and 'href' in li.find('a').attrs:
                href = 'https://www.asos.com/' + li.find('a')['href']
                product_id = extract_asos_product_id(href)

                image_link_element = li.select_one('img')
                print(image_link_element)

                product_title_div = li.find('div', class_='productTitle_gn7x9')

                if product_title_div:
                    name = product_title_div.find('p').text.strip()
                    data['Name'].append(name)
                else:
                    data['Name'].append(None)

                if image_link_element:
                    image_link = extract_image_link(image_link_element)
                    data['Image Link'].append(image_link)
                else:
                    data['Image Link'].append(None)

                data['Link'].append(href)
                data['Id'].append(product_id)

        data_df = pd.DataFrame(data)
        print(data_df[['Name', 'Image Link']])
        return data_df

    finally:
        driver.quit()


def id_list_to_price_list(product_id_list):
    product_list = []
    for product_id in product_id_list:
        url = build_request_link(product_id)
        time.sleep(1)  # 1-second delay
        product_name, product_prices = extract_info_codembo_url(url)
        product_list.append((product_name, product_prices))

    return product_list


def can_use_il17(df, sum_df):
    min_cost_eur = convert_currency(50, '£', 'EUR')

    if (sum_df['IL'] > min_cost_eur).all():
        sum_df['IL'] = (sum_df['IL'] * 0.83).round(2)
        df['IL'] = (df['IL'] * 0.83).round(2)

    return df, sum_df


def split_products_into_baskets(products_df, min_value, max_value):
    sorted_products = products_df.sort_values(by=['product_name', 'Cheapest_Price'])
    n = len(sorted_products)
    dp = [float('inf')] * (n + 1)
    dp[0] = 0

    for i in range(1, n + 1):
        current_basket_value = 0
        max_price_in_basket = 0

        for j in range(i, 0, -1):
            current_basket_value += sorted_products.iloc[j - 1]['Cheapest_Price']
            max_price_in_basket = max(max_price_in_basket, sorted_products.iloc[j - 1]['Cheapest_Price'])

            if current_basket_value <= max_value and max_price_in_basket <= max_value:
                dp[i] = min(dp[i], dp[j - 1] + 1)

    result = []
    i = n
    while i > 0:
        j = i
        while j > 0 and dp[j] == dp[i]:
            j -= 1

        basket_products = sorted_products.iloc[j:i]
        basket_total_price = basket_products['Cheapest_Price'].sum().round(2)

        result.append({
            'Basket': result[::-1],
            'Country': basket_products['Country'].values[0],
            'Total_Price': basket_total_price,
            'Products': basket_products[['product_name', 'Cheapest_Price']].to_dict(orient='records')
        })
        i = j

    return result[::-1]


def printb(result):
    for i, basket in enumerate(result, start=1):
        print(f'Basket {i}:')
        print(f'Country: {basket["Country"]}')
        print(f'Total Price: {basket["Total_Price"]}')
        print('Products:')
        for product in basket['Products']:
            print(f'  {product["product_name"]}: {product["Cheapest_Price"]}')
        print()


def send_to_israel(url):
    if not is_valid_asos_product_link(url):
        print("Not a valid ASOS link")
        return "Invalid Link"

    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_argument("--enable-logging")  # Enable browser logging
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    path = os.getenv('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(path, options=options)

    try:
        driver.get(url)

        name_element = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "jcdpl"))
        )

        name_text = name_element.get_attribute("innerText").strip()
        print("Product Name:", name_text)

        shipping_restrictions_button = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[@data-testid='deliveryAndReturns__shippingRestrictionsButton']")
            )
        )
        if shipping_restrictions_button:
            shipping_restrictions_button.click()

            shipping_restrictions_list = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//ul[@class='Uu_Pi' and @data-testid='shipping-restrictions-country-list']")
                )
            )

            # Check if 'Israel' is in the shipping restrictions list
            if 'Israel' in shipping_restrictions_list.text:
                print("This product can be sent to Israel.")
                return True
            else:
                print("This product cannot be sent to Israel.")
                return False
        else:
            print("This product can be sent to Israel.")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error"

    finally:
        # Close the WebDriver
        driver.quit()


def split_and_print_basket(result_df):
    customs_payment_limit = convert_currency(75, '$', 'EUR')

    country_list = result_df["Country"].unique()
    for country in country_list:
        result_df_country = result_df[result_df["Country"] == country]
        printb(split_products_into_baskets(result_df_country, 50, customs_payment_limit))


def handle_product_basket_search(product_url):
    data = extract_product_id_from_url(product_url)

    return data


def extract_image_link(html_code):
    # Check if html_code is not None
    if html_code:
        # Access the 'src' attribute of the <img> tag
        src_attribute = html_code.get('src')

        # Check if 'src' attribute is found
        if src_attribute:
            return src_attribute

    # Return None if 'src' attribute is not found or html_code is None
    return None
