from dotenv import load_dotenv
import os
from analyze import analyze_stock, send_to_openai, format_and_print_response
from utils import cleanup_files

load_dotenv()

def main():
    symbols = input("Enter the stock ticker symbols (comma-separated): ").split(',')
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    news_api_key = os.getenv("NEWS_API_KEY")
    openai_key = os.getenv("OPEN_AI_API_KEY")
    if not openai_key or not alpha_vantage_key or not news_api_key:
        missing_keys = []
        if not openai_key:
            missing_keys.append("OPEN_AI_API_KEY")
        if not alpha_vantage_key:
            missing_keys.append("ALPHA_VANTAGE_API_KEY")
        if not news_api_key:
            missing_keys.append("NEWS_API_KEY")
        raise ValueError(f"Missing API keys: {', '.join(missing_keys)}")

    all_analysis_data = []
    for symbol in symbols:
        symbol = symbol.strip()
        analysis_data = analyze_stock(symbol, alpha_vantage_key, news_api_key, openai_key)
        all_analysis_data.append(analysis_data)
        cleanup_files(symbol)

    chatgpt_response = send_to_openai(all_analysis_data, openai_key)
    format_and_print_response(chatgpt_response)

if __name__ == "__main__":
    main()
