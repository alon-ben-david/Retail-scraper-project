import collections.abc
import requests


def convert_currency(amount, from_currency, to_currency):
    api_url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    supported_currencies = ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP', 'HKD', 'HUF', 'IDR',
                            'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK',
                            'SGD', 'THB', 'TRY', 'USD', 'ZAR']
    if from_currency in supported_currencies and to_currency in supported_currencies:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            converted_amount = data['rates'][to_currency]
            return converted_amount

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Frankfurter API: {e}")
            return None

    else:
        return False
