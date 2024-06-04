import requests
import pandas as pd

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
    return response.json()

def fetch_news_articles(symbol, api_key):
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()
