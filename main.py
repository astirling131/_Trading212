from clients.trading212 import Trading212Client
from clients.yfinance import YFinanceClient

def launch_app():

    # 1. Trading212 Client Usage
    print("--- Starting Trading212 Scrape ---")
    client001 = Trading212Client(is_demo=False)
    client001.fetch_account_cash()
    client001.download_historic_data()

    # 2. YFinanceClient Client Usage
    print("\n--- Starting YFinance Scrape ---")
    client002 = YFinanceClient()
    client002.get_tickers()

# Execution control
if __name__ == "__main__":

    # launch the app
    launch_app()
