########################################################################################################################
## Python Script to Download Data from Trading212 using API key                                                       ##
##                                                                                                                    ## 
## Author: Andrew Stirling                                                                                            ##
## Date: 2025-12-28                                                                                                   ##
## Description: This script connects to the Trading212 API using a provided API key to download trading data.         ##
## Requirements: requests library                                                                                     ##
## Usage: python main.py                                                                                              ##
########################################################################################################################

#################
# CONFIGURATION #
#################

# import necessary libraries
import requests
import base64
import time
import pandas as pd
import os
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from twelvedata import TDClient

# function to get the api key and secret from the .env file
def _get_api_keys(provider: str) -> Tuple[str, str]:
    # initialize variables
    api_key_id, api_secret = None, None
    # run inside a try block for error handling
    try:
        # Check the requested provider
        if provider == "Trading212":
            # load data from the .env file into variables
            with open(".env", "r") as file:
                for line in file:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        if parts[0] == "T212_API_KEY":
                            api_key = parts[1]
                        elif parts[0] == "T212_API_SECRET":
                            api_secret = parts[1]
            return api_key, api_secret
        elif provider == "TwelveData":
            # load data from the .env file into 'file' variable
            with open(".env", "r") as file:
                for line in file:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        if parts[0] == "TWD_API_KEY":
                            api_key = parts[1]
            return api_key, None
    # catch file not found error
    except FileNotFoundError:
        # print an error message if the .env file is missing
        print("\nError: .env file not found!")
        # return None to the function caller to indicate failure
        return None, None
        
##############
# T212 CLASS #
##############

class Trading212Client:

    # define the specific api endpoints
    ENDPOINT_CASH = "/equity/account/cash"
    ENDPOINT_HISTORY = "/equity/history/exports"

    # class constructor
    def __init__(self, is_demo: bool = False):
        # define the URL we want to 'call'.
        if is_demo:
           self.url = "https://demo.trading212.com/api/v0"
        else:
           self.url = "https://live.trading212.com/api/v0"
        self.headers = self._set_auth_header()

    ##~~~~~~~~~~~~~~~~~~
    ## HELPER FUNCTIONS
    ##~~~~~~~~~~~~~~~~~~

    # function to set the authorization header for requests
    def _set_auth_header(self) -> Dict[str, str]:
        # get the T212 api keys from the .env file
        key_id, secret_key = _get_api_keys("Trading212")
        # exit the function if we didn't get a key
        if not key_id or not secret_key:
            print("\nError: Credentials missing in .env file.")
            return
        # create the authorization header value and encode to UTF-8 (bytes)
        credentials_string = f"{key_id}:{secret_key}"
        raw_bytes = credentials_string.encode("utf-8")
        # encode the bytes to Base64 then back to useable string
        base64_bytes = base64.b64encode(raw_bytes)
        base64_string = base64_bytes.decode("utf-8")
        # format the final authorization header value
        auth_header_value = f"Basic {base64_string}"
        headers = {
            "Authorization": auth_header_value
        }
        return headers

    # function to make HTTP requests
    def _make_request(self, method: str, endpoint: str, payload: Optional[dict] = None) -> Any:
        # construct the full URL
        url = self.url + endpoint
        print(f"\nSending {method} request to: {endpoint}")
        # check if headers are set
        if not self.headers:
            print("Headers not set, check API keys")
            return None
        # run inside a try catch block for error handling
        try:
            # perform the HTTP request based on the method
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=payload)
            else:
                raise ValueError("Unsupported HTTP request")
            # check the response status code
            if response.status_code == 200:
                # on successful request return the JSON data
                return response.json()
            else:
                # on failed request print the status code and reason
                print(f"Request failed. Status: {response.status_code}")
                print(f"Reason: {response.text}")
                return None
        # catch any exceptions that occur during the request
        except Exception as e:
            print(f"An error occurred during request: {e}")
            return None

    # function to poll for report completion
    def _poll_for_completion(self, report_id: int) -> Optional[str]:
        # define the endpoint
        endpoint = self.ENDPOINT_HISTORY
        # set loop variable
        attempts: int = 10
        count: int = 1
        # run inside a try catch block for error handling
        try:
            # loop until max attempts
            while count < attempts:
                print(f"Checking status, attempt {count} of {attempts}...")
                # perform GET request on endpoint
                exports = self._make_request("GET", endpoint)
                # wait before next attempt
                time.sleep(5)
                # check if the request returned any exports
                if exports:
                    target_report = None
                    # find the report with the matching report ID
                    for report in exports:
                        if report.get("reportId") == report_id:
                            target_report = report
                            #  exit the loop early if theres no report to wait for
                            break
                    # make sure it found the target report
                    if target_report:
                        status = target_report.get("status")
                        # check if the report is finished
                        if status == "Finished":
                            print(f"Status is {status}")
                            # return the download link
                            return target_report.get("downloadLink")
                        # wait 5 seconds before next loop iteration if report is not ready to download
                        time.sleep(5)
        # catch any exceptions that occur during polling
        except Exception as e:
            print(f"An error occurred while polling for report completion: \n{e}")
            return None
        # if we reach here it timed out
        print("\nTimed out waiting on report")
        return None
    
    ##~~~~~~~~~~~~~~~~~~
    ## CLASS FUNCTIONS
    ##~~~~~~~~~~~~~~~~~~

    # function to fetch account cash data
    def fetch_account_cash(self) -> None:
        endpoint = self.ENDPOINT_CASH
        data = self._make_request("GET", endpoint)
        # wait for response from requeest
        time.sleep(5)
        if data:
            print(f"\n---CASH DATA---")
            print(data)

    # function to download history report
    def download_historic_data(self) -> None:
        endpoint = self.ENDPOINT_HISTORY
        # set from and to date for history reports
        now = datetime.now(timezone.utc)
        sdt = now - timedelta(weeks=4)
        time_from = sdt.strftime("%Y-%m-%dT%H:%M:%SZ")
        time_to = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        # set payload
        payload = {
          "dataIncluded": {
            "includeDividends": True,
            "includeInterest": True,
            "includeOrders": True,
            "includeTransactions": True
            },
          "timeFrom": time_from,
          "timeTo": time_to
        }
        # perform POST request on endpoint
        response = self._make_request("POST", endpoint, payload)
        time.sleep(5)
        if not response or "reportId" not in response:
            print("Failed to get Report ID")
            return
        report_id = response.get("reportId")
        print(f"Report ID: {report_id}")
        download_link = self._poll_for_completion(report_id)
        if download_link:
            print("\nDownloading .csv report...")
            df = pd.read_csv(download_link)
            if not df.empty:
                filename = f"History Report {report_id}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved to {filename}")
            else:
                print(".csv report was empty.")

##################
# YFinance CLASS #
##################

class YFinanceClient:

    # class constructor
    def __init__(self):
        pass

    # function to get historic market data  
    def get_historic_data(self, symbol: str, interval: str = "15m", period: str = "1mo") -> None:
        print(f"\n--- Fetching {interval} data for {symbol} ---")
        if symbol in ["CSP1", "VHYL", "IDVY"] and not symbol.endswith(".L"):
            symbol = f"{symbol}.L"
        try:
            df = yf.download(
                tickers=symbol, 
                interval=interval, 
                period=period,
                progress=False
            )
            if not df.empty:
                # Yahoo returns complex MultiIndex columns sometimes
                df.reset_index(inplace=True)
                # Save to Disk
                folder = "market_data"
                os.makedirs(folder, exist_ok=True)
                filename = f"{folder}/{symbol}_{interval}.csv"
                df.to_csv(filename, index=False)
                print(f"Success! Saved {len(df)} rows to {filename}")
                print(df.head(3))
            else:
                print(f"Error: No data found for {symbol}")
        except Exception as e:
            print(f"An error occurred: {e}")
     
##################
# MAIN EXECUTION #
##################

# Execution control
if __name__ == "__main__":

    # 1. Trading212 Client Usage
    client001 = Trading212Client(is_demo=False)
    client001.fetch_account_cash()
    client001.download_historic_data()

    # 2. YFinanceClient Client Usage
    client002 = YFinanceClient()
    client002.get_historic_data(symbol="CSP1")
    
