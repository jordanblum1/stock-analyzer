import matplotlib.pyplot as plt
import json
from openai import OpenAI
import threading
from fetch_data import fetch_historical_data, fetch_fundamentals, fetch_news_articles
from summarize import summarize_article
from utils import loading_indicator

def analyze_stock(symbol, alpha_vantage_key, news_api_key, openai_key):
    print(f"Fetching historical data for {symbol}...")
    historical_data = fetch_historical_data(symbol, alpha_vantage_key)
    print("Historical data fetched.")

    print(f"Fetching fundamentals for {symbol}...")
    fundamentals = fetch_fundamentals(symbol, alpha_vantage_key)
    print("Fundamentals fetched.")

    print(f"Fetching news articles for {symbol}...")
    news_data = fetch_news_articles(symbol, news_api_key)
    print("News articles fetched.")

    print("Summarizing news articles...")
    summarized_news = []
    articles_to_summarize = news_data['articles'][:5]  # Fetch only the first 5 articles
    for i, article in enumerate(articles_to_summarize):
        print(f"Summarizing article {i+1}/{len(articles_to_summarize)}: {article['title']}")
        try:
            summary = summarize_article(article['content'], openai_key)
            summarized_news.append({
                "title": article['title'],
                "summary": summary,
                "url": article['url']
            })
            print(f"Article {i+1} summarized successfully.")
        except Exception as e:
            print(f"Error summarizing article {i+1}: {e}")
    print("News articles summarized.")

    print("Calculating moving averages...")
    historical_data['50_MA'] = historical_data['4. close'].rolling(window=50).mean()
    historical_data['200_MA'] = historical_data['4. close'].rolling(window=200).mean()
    print("Moving averages calculated.")

    print("Generating plot...")
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
    print("Plot generated and saved.")

    print("Compiling analysis data...")
    analysis_data = {
        "symbol": symbol,
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
        },
        "news_summaries": summarized_news
    }
    print("Analysis data compiled.")

    print("Saving analysis data to files...")
    with open(f'{symbol}_analysis.json', 'w') as json_file, open(f'{symbol}_analysis.txt', 'w') as text_file:
        json.dump(analysis_data, json_file, indent=4)
        text_file.write(json.dumps(analysis_data, indent=4))
    print("Analysis data saved.")

    return analysis_data


def send_to_openai(analysis_data, api_key):
    print("Initializing OpenAI client...")
    client = OpenAI(api_key=api_key)

    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_indicator, args=(stop_event,))
    loader_thread.start()

    print("Sending data to OpenAI for analysis...")
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Analyze and rank the following stock data"},
            {"role": "user", "content": json.dumps(analysis_data)}
        ],
        model="gpt-4o"
    )
    stop_event.set()
    loader_thread.join()
    print("Received response from OpenAI.")

    return response

def format_and_print_response(chatgpt_response):
    print("\nResponse from OpenAI ChatGPT:\n")
    for choice in chatgpt_response.choices:
        content = choice.message.content
        paragraphs = content.split('\n')
        for paragraph in paragraphs:
            if "bearish" in paragraph or "bullish" in paragraph:
                print(f"\033[1m{paragraph}\033[0m")
            else:
                print(paragraph)
