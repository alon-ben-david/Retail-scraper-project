import collections.abc
import requests

currency_symbols = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'ILS': '₪',
    'PLN': 'zł',
    'CHF': 'Fr.'

}


def convert_currency(amount, from_currency, to_currency):
    if from_currency in currency_symbols.values():
        from_currency = get_currency_code(from_currency, currency_symbols)

    if to_currency in currency_symbols.values():
        to_currency = get_currency_code(to_currency, currency_symbols)

    api_url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"

    supported_currencies = ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK',
                            'DKK', 'EUR', 'GBP', 'HKD', 'HUF', 'IDR',
                            'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN',
                            'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON',
                            'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']
    if from_currency not in supported_currencies:
        # Handle unsupported from_currency
        print(f"Unsupported from_currency: {from_currency}")
        return None

    if to_currency not in supported_currencies:
        # Handle unsupported to_currency
        print(f"Unsupported to_currency: {to_currency}")
        return None

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        converted_amount = data['rates'][to_currency]

        return converted_amount

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

    return False


def get_currency_code(symbol, currency_symbols):
    if symbol in currency_symbols.values():
        # Find the key (currency code) corresponding to the given symbol
        for code, sym in currency_symbols.items():
            if sym == symbol:
                return code
    else:
        # Handle the case when the symbol is not found in currency_symbols
        return None
