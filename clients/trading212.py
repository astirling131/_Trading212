import base64
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from config import get_api_keys

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
    def _set_auth_header(self) -> Optional[Dict[str, str]]:
        # get the T212 api keys from the .env file
        key_id, secret_key = get_api_keys("Trading212")
        # exit the function if we didn't get a key
        if not key_id or not secret_key:
            raise ValueError("Credentials missing in .env file.")
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
            raise ValueError("Headers not set, check API keys")
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
                error_msg = f"Request failed. Status: {response.status_code} Reason: {response.text}"
                print(error_msg)
                raise Exception(error_msg)
        # catch any exceptions that occur during the request
        except Exception as e:
            print(f"An error occurred during request: {e}")
            raise e

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
                # wait 5 seconds before HTTP request to avoid multiple calls in short succession
                time.sleep(5)
                # perform GET request on endpoint
                exports = self._make_request("GET", endpoint)
                # wait before next attempt
                time.sleep(5)
                # Check for a 'too many requests' error and break if so
                if exports == 429:
                    print("Rate limit exceeded, waiting longer before trying again...")
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
                count += 1
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
    def fetch_account_cash(self) -> Any:
        endpoint = self.ENDPOINT_CASH
        data = self._make_request("GET", endpoint)
        # wait for response from requeest
        time.sleep(2) # Reduced from 5 for snappier UI, can adjust back if rate limited
        # Check for a 'too many requests' error and break if so
        if data == 429:
            print("Rate limit exceeded, try again later.")
            return None
        if data:
            print(f"\n---CASH DATA---")
            print(data)
            return data
        return None

    # function to download history report
    def download_historic_data(self) -> Optional[str]:
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
        time.sleep(2)        
        # Check for a 'too many requests' error and break if so
        if response == 429:
            print("Rate limit exceeded, try again later.")
            return None
        # check if a report id was in the response
        if not response or "reportId" not in response:
            print("Failed to get Report ID")
            return None
        report_id = response.get("reportId")
        print(f"Report ID: {report_id}")
        # poll for the download to complete and get report link
        download_link = self._poll_for_completion(report_id)
        if download_link:
            print("\nDownloading .csv report...")
            # read report into a dataframe
            df = pd.read_csv(download_link)
            # check report was not empty
            if not df.empty:
                # set filename
                filename = f"History Report {report_id}.csv"
                # save report
                df.to_csv(filename, index=False)
                print(f"Saved to {filename}")
                return filename
            else:
                # warn user if report was empty
                print(".csv report was empty.")
                return None
        return None
