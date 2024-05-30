import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
from openai import OpenAI
import threading
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_historical_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['Time Series (Daily)']).T
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def fetch_fundamentals(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json()

def analyze_stock(symbol, api_key):
    historical_data = fetch_historical_data(symbol, api_key)
    fundamentals = fetch_fundamentals(symbol, api_key)

    # Technical analysis
    historical_data['50_MA'] = historical_data['4. close'].rolling(window=50).mean()
    historical_data['200_MA'] = historical_data['4. close'].rolling(window=200).mean()

    # Plot closing price and moving averages
    plt.figure(figsize=(12, 6))
    plt.plot(historical_data.index, historical_data['4. close'], label='Closing Price', color='blue')
    plt.plot(historical_data.index, historical_data['50_MA'], label='50-day MA', color='orange')
    plt.plot(historical_data.index, historical_data['200_MA'], label='200-day MA', color='green')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{symbol} Historical Price and Moving Averages')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{symbol}_historical_chart.png')

    # Prepare data for GPT-4 analysis
    analysis_data = {
        "technical_analysis": {
            "50_MA": historical_data['50_MA'].iloc[-1],
            "200_MA": historical_data['200_MA'].iloc[-1],
            "current_price": historical_data['4. close'].iloc[-1]
        },
        "fundamental_analysis": {
            "Company Name": fundamentals.get('Name'),
            "Market Cap": fundamentals.get('MarketCapitalization'),
            "PE Ratio": fundamentals.get('PERatio'),
            "ROE": fundamentals.get('ReturnOnEquityTTM'),
            "EPS": fundamentals.get('EPS'),
            "Dividend Yield": fundamentals.get('DividendYield'),
            "52 Week High": fundamentals.get('52WeekHigh'),
            "52 Week Low": fundamentals.get('52WeekLow')
        }
    }

    # Save data to JSON file
    with open(f'{symbol}_analysis.json', 'w') as json_file, open(f'{symbol}_analysis.txt', 'w') as text_file:
        json.dump(analysis_data, json_file, indent=4)
        text_file.write(json.dumps(analysis_data, indent=4))

    return analysis_data

def loading_indicator(stop_event):
    print("Sending data to OpenAI for analysis", end="")
    while not stop_event.is_set():
        print(".", end="")
        sys.stdout.flush()
        time.sleep(1)
    print()  # Move to the next line after loading

def send_to_openai(analysis_data, api_key):
    client = OpenAI(api_key=api_key)

    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_indicator, args=(stop_event,))
    loader_thread.start()

    response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "Analyze stock data"},
        {"role": "user", "content": json.dumps(analysis_data)}
    ],
    model="gpt-4"
    )
    stop_event.set()
    loader_thread.join()  # Wait for the loading indicator to finish
    return response

def cleanup_files(symbol):
    os.remove(f"{symbol}_analysis.json")
    os.remove(f"{symbol}_analysis.txt")
    os.remove(f"{symbol}_historical_chart.png")

def format_and_print_response(chatgpt_response):
    print("\nResponse from OpenAI ChatGPT:\n")
    for choice in chatgpt_response.choices:
        content = choice.message.content
        # Split the response into paragraphs for better readability
        paragraphs = content.split('\n')
        for paragraph in paragraphs:
            if "bearish" in paragraph or "bullish" in paragraph:
                # Highlight key terms and analysis
                print(f"\033[1m{paragraph}\033[0m")
            else:
                print(paragraph)

def main():
    symbol = input("Enter the stock ticker symbol: ")
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    openai_key = os.getenv("OPEN_AI_API_KEY")

    if not openai_key or not alpha_vantage_key:
        missing_keys = []
        if not openai_key:
            missing_keys.append("OPEN_AI_API_KEY")
        if not alpha_vantage_key:
            missing_keys.append("ALPHA_VANTAGE_API_KEY")
        print(f"Missing environment variables: {', '.join(missing_keys)}. Please set them.")
        return

    analysis_data = analyze_stock(symbol, alpha_vantage_key)

    # Display summary of analysis
    print("\nTechnical Analysis:")
    print(f"Current Price: {analysis_data['technical_analysis']['current_price']}")
    print(f"50-day MA: {analysis_data['technical_analysis']['50_MA']}")
    print(f"200-day MA: {analysis_data['technical_analysis']['200_MA']}")

    print("\nFundamental Analysis:")
    for key, value in analysis_data['fundamental_analysis'].items():
        print(f"{key}: {value}")

    print(f"\nAnalysis data has been saved to {symbol}_analysis.json and {symbol}_analysis.txt.\n")
    
    chatgpt_response = send_to_openai(analysis_data, openai_key)
    format_and_print_response(chatgpt_response)
    cleanup_files(symbol)

if __name__ == "__main__":
    main()
