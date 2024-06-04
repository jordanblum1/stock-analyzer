import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_historical_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
    response = requests.get(url)
    data = response.json()
    if 'Time Series (Daily)' not in data:
        error_message = data.get('Error Message', 'No specific error message provided.')
        note = data.get('Note', '')
        if not error_message and not note:
            error_message = "Unexpected API response format."
        raise ValueError(f"Error fetching historical data for {symbol}: {error_message} {note}")
    df = pd.DataFrame(data['Time Series (Daily)']).T
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def fetch_fundamentals(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    if not data:
        raise ValueError(f"Error fetching fundamentals for {symbol}: No data returned")
    return data

def fetch_news(symbol, news_api_key):
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={news_api_key}"
    response = requests.get(url)
    news_data = response.json()
    if 'articles' not in news_data:
        error_message = news_data.get('message', 'No specific error message provided.')
        raise ValueError(f"Error fetching news for {symbol}: {error_message}")
    return news_data['articles'][:5]  # Return top 5 news articles

def test_api_endpoints(symbol):
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    news_api_key = os.getenv("NEWS_API_KEY")

    try:
        print(f"Testing historical data for {symbol}")
        historical_data = fetch_historical_data(symbol, alpha_vantage_key)
        print(historical_data.head())
    except Exception as e:
        print(e)

    try:
        print(f"\nTesting fundamentals data for {symbol}")
        fundamentals = fetch_fundamentals(symbol, alpha_vantage_key)
        print(fundamentals)
    except Exception as e:
        print(e)

    try:
        print(f"\nTesting news data for {symbol}")
        news = fetch_news(symbol, news_api_key)
        for article in news:
            print(article['title'])
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test_stock_symbol = "AAPL"  # Change to "NVDA" or any other stock symbol to test
    test_api_endpoints(test_stock_symbol)
