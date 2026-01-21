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
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple

##############
# T212 CLASS #
##############

class Trading212Client:

    # define the specific api endpoints
    ENDPOINT_CASH = "/equity/account/cash"
    ENDPOINT_HISTORY = "/equity/history/exports"
    ENDPOINT_TICKER = "/equity/ / "

    def __init__(self, is_demo: bool = False):
        # define the URL we want to 'call'.
        if is_demo:
           self.url = "https://demo.trading212.com/api/v0"
        else:
           self.url = "https://live.trading212.com/api/v0"
        self.headers = self._set_auth_header()

    def _get_api_keys(self) -> Tuple[str, str]:
        # get the api key and secret from the .env file
        api_key_id = None
        api_secret = None
        # run inside a try block for error handling
        try:
            # load data from the .env file into 'file' variable
            with open(".env", "r") as file:
                for line in file:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        if parts[0] == "T212_API_KEY":
                            api_key = parts[1]
                        elif parts[0] == "T212_API_SECRET":
                            api_secret = parts[1]
            return api_key, api_secret

        # catch file not found error
        except FileNotFoundError:
            # print an error message if the .env file is missing
            print("\nError: .env file not found!")
            # return None to the function caller to indicate failure
            return None, None

    def _set_auth_header(self) -> Dict[str, str]:
        # add the api_key to a variable for use in the function
        key_id, secret_key = self._get_api_keys()
        # exit the function if we didn't get a key
        if not key_id or not secret_key:
            print("\nError: Credentials missing in .env file.")
            return
        # create the authorization header value
        credentials_string = f"{key_id}:{secret_key}"
        # encode the string credentials to UTF-8 (bytes)
        raw_bytes = credentials_string.encode("utf-8")
        # encode the bytes to Base64 then back to useable string
        base64_bytes = base64.b64encode(raw_bytes)
        base64_string = base64_bytes.decode("utf-8")
        # format the final authorization header value
        auth_header_value = f"Basic {base64_string}"
        # create the headers dictionary for the GET request
        headers = {
            "Authorization": auth_header_value
        }
        return headers

    def _make_request(self, method: str, endpoint: str, payload: Optional[dict] = None) -> Any:
        url = self.url + endpoint
        print(f"\nSending {method} request to: {endpoint}")
        if not self.headers:
            print("Headers not set, check API keys")
            return None
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=payload)
            else:
                raise ValueError("Unsupported HTTP request")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request failed. Status: {response.status_code}")
                print(f"Reason: {response.text}")
                return None

        except Exception as e:
            print(f"An error occurred during request: {e}")
            return None

    def _poll_for_completion(self, reportid: int) -> Opti>
        endpoint = self.ENDPOINT_HISTORY
        # set loop variable
        attempts: int = 10
        count: int = 1
        while count < attempts:
            print(f"\nChecking status, attempt {count} of>
            exports = self._make_request("GET", endpoint)
            time.sleep(5)
            if exports:
                target_report = None
                for report in exports:
                    if report.get("reportId") == reportid:
                        target_report = report
                        break
                if target_report:
                    status = target_report.get("status")
                    if status == "Finished":
                        print(f"Status is {status}")
                        return target_report.get("downloa>
                    time.sleep(5)
        print("\nTimed out waiting on report")
        return None

    ##################
    # MAIN EXECUTION #
    ##################

    # function to fetch account cash data
    def fetch_account_cash(self) -> None:
        endpoint = self.ENDPOINT_CASH
        data = self._make_request("GET", endpoint)
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
        reportid = response.get("reportId")
        print(f"Report ID: {reportid}")
        download_link = self._poll_for_completion(reportid)
        if download_link:
            print("\nDownloading .csv report...")
            df = pd.read_csv(download_link)
            if not df.empty:
                filename = f"History Report {reportid}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved to {filename}")
            else:
                print(".csv report was empty.")

    def download_ticker_data(self) -> None:
        endpoint = self.ENDPOINT_TICKER
        
#####################
# EXECUTION CONTROL #
#####################

# This line ensures the script runs only when executed directly (if the .py script is imported the __name__ variable will be just 'main' and not '__main__')
if __name__ == "__main__":
    client = Trading212Client(is_demo=False)
    client.fetch_account_cash()
    client.download_historic_data()
    client.downloaf_ticker_data()

