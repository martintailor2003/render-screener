import requests
import numpy as np
import logging
import time
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_historical_data(pair, interval='1h', limit=50):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={pair}&interval={interval}&limit={limit}"
    try:
        logging.debug(f"Fetching data for {pair}")
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch data for {pair}: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {pair}: {e}")
        time.sleep(60)
        return None

def calculate_volatility_to_close_percentage(data):
    closes = np.array([float(entry[4]) for entry in data])  # Extract closing prices
    log_returns = np.log(closes / np.roll(closes, 1))  # Calculate logarithmic returns
    volatility = np.std(log_returns) * np.sqrt(50) * 100  # Compute annualized volatility
    return volatility

def select_top_pairs_with_highest_volatility(pairs, top_n=10):
    pairs_with_volatility = []
    for pair in pairs:
        historical_data = fetch_historical_data(pair)
        if historical_data and len(historical_data) >= 50:  # Ensure enough data points for calculation
            volatility = calculate_volatility_to_close_percentage(historical_data)
            pairs_with_volatility.append((pair, volatility))

    pairs_with_volatility.sort(key=lambda x: x[1], reverse=True)  # Sort pairs by volatility
    return pairs_with_volatility[:top_n]


def get_pairs():
     # Fetch all USDT futures pairs from Binance
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        logging.debug("Fetching exchange info")
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        
        if response.status_code == 200:
            exchange_info = response.json()
            usdt_pairs = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['quoteAsset'] == 'USDT']
            logging.debug(usdt_pairs)
        else:
            logging.error(f"Failed to fetch exchange info: HTTP {response.status_code}")
            usdt_pairs = []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching exchange info: {e}")
        usdt_pairs = []

    return usdt_pairs