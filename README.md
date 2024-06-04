# stock-analyzer

This is a simple stock analyzer. It uses the Vantage API, OpenAI API & a News API to get the latest data & perform a sentiment analysis on price, date, and volume, etc. It allows for multiple stocks to be analyzed at once and summarizes the news articles and fundamentals to rank the stocks given and why it believes the stock should be at that rank.

# to-do
- potentially make a ui for this
- clean up the logging
- add a way to save the results to a file &/or memoize the results

# how to run
1. create python virtual environment
    - `python -m venv env && source env/bin/activate`
2. install the requirements.txt
    - `pip install -r requirements.txt`
3. set the environment variables in a `.env` file
    - `OPEN_AI_API_KEY=<your_open_ai_api_key>`
    - `ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_api_key>`
    - `NEWS_API_KEY=<your_news_api_key>`
4. run the `python stock-analyzer.py` file
5. profit
