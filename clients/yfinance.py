import time
import os
import pandas as pd
from yahooquery import Ticker

class YFinanceClient:

    # class constructor
    def __init__(self):
        pass

    # yahooquery
    def _yahooquery(self, ticker: str, interval: str, period: str) -> pd.DataFrame:
        try:
            # set the ticker using yahooquery
            t = Ticker(ticker)
            # create dataframe with ticker data
            df = t.history(period=period, interval=interval)
            # return an empty dataframe if an empty dictionary returned
            if isinstance(df, dict) or df.empty:
                return pd.DataFrame()
            df.reset_index(inplace=True)
            # return the ticker data as dataframe
            return df
        except Exception as e:
            print(f"\nError fetching {ticker}: {e}")
            # return empty dataframe on error
            return pd.DataFrame()

    # get the ticker symbols from the csv
    def get_tickers(self, filename: str = "tickers.csv", col_index: int = 2):
        # read list of tickers
        try:
            data = pd.read_csv(filename, header=0, usecols=[col_index])
            # loop through each and call download function
            for row in data.itertuples(index=False, name=None):
                value = str(row[0])
                try:
                    # download ticker data
                    self.download_data(value)
                    # sleep to avoid multiple calls in short succession
                    time.sleep(1)
                except Exception as e:
                    # warn the user if there was an error
                    print(f"\nError processing ticker {value}: {e}")
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            raise ValueError(f"{filename} not found.")
        except pd.errors.EmptyDataError:
             print(f"Error: {filename} is empty.")
             raise ValueError(f"{filename} is empty.")
        except Exception as e:
            print(f"Error reading csv: {e}")
            raise e

    # function to get historic market data
    def download_data(self, symbol: str, interval: str = "15m", period: str = "1mo") -> None:
        from utils.data_transform import transform_yfinance_data

        print(f"\nFetching {interval} data for {symbol}...")
        # add the .l for known lse stocks
        if symbol in ["CSP1", "VHYL", "XMWX", "IGL5"] and not symbol.endswith(".L"):
            symbol = f"{symbol}.L"
        try:
            # run the yahoo query
            df = self._yahooquery(symbol, interval, period)
            if not df.empty:
                # Transform data for user-friendly display
                df = transform_yfinance_data(df)

                # Save to Disk
                folder = "market_data"
                # create folder if dosent exist
                os.makedirs(folder, exist_ok=True)
                # set filename
                filename = f"{folder}/{symbol}_{interval}.csv"
                # save the report
                df.to_csv(filename, index=False)
                print(f"Success! Saved {len(df)} rows to {filename}")
            else:
                # warn the user if no data returned
                print(f"Error: No data found for {symbol}")
        except Exception as e:
            # warn the user if an error occurred
            print(f"An error occurred: {e}")
