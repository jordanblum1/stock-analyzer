# stock-analyzer

This is a simple stock analyzer. It uses the Vantage API & OpenAI API to get the latest data & perform a sentiment analysis on price, date, and volume, etc.

# to-do
- get the latest news on the stock
- allow it to loop through a list of stocks and find the best vs the worst
- potentially make a ui for this

# how to run
1. create python env
    - `python -m venv env && source env/bin/activate`
2. install the requirements.txt
    - `pip install -r requirements.txt`
3. set the environment variables in a `.env` file
    - `OPEN_AI_API_KEY=<your_open_ai_api_key>`
    - `ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_api_key>`
4. run the `python stock-analyzer.py` file
5. profit
