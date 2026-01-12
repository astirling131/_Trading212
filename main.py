########################################################################################################################
## Python Script to Download Data from Trading212 using API key                                                       ##
##                                                                                                                    ## 
## Author: Andrew Stirling                                                                                            ##
## Date: 2025-12-28                                                                                                   ##
## Description: This script connects to the Trading212 API using a provided API key to download trading data.         ##
## Requirements: requests library                                                                                     ##
## Usage: python main.py                                                                                 ##
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

# define the URL we want to 'call'.
BASE_URL = "https://live.trading212.com/api/v0"
# define the specific endpoint for account cash data
ENDPOINT_CASH = "/equity/account/cash"
ENDPOINT_HISTORY = "/equity/history/exports"


####################
# HELPER FUNCTIONS #
####################

# function to read the API key from .env file
def get_api_key():

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
        print("Error: .env file not found!")
        # return None to the function caller to indicate failure
        return None, None



##################
# MAIN EXECUTION #
##################

# function to fetch account cash data
def fetch_account_cash():

    ##########
    ## CASH ##
    ##########

    # add the api_key to a variable for use in the function
    key_id, secret_key = get_api_key()

    # exit the function if we didn't get a key
    if not key_id or not secret_key:
        print(" ")
        print(" ")
        print("Error: Credentials missing in .env file.")
        return

    # create the authorization header value
    credentials_string = f"{key_id}:{secret_key}"

    # encode the credentials to UTF-8
    raw_bytes = credentials_string.encode("utf-8")

    # encode the bytes to Base64
    base64_bytes = base64.b64encode(raw_bytes)

    # decode the Base64 bytes back to a string
    base64_string = base64_bytes.decode("utf-8")

    # format the final authorization header value
    auth_header_value = f"Basic {base64_string}"

    # create the headers dictionary for the GET request
    headers = {
        "Authorization": auth_header_value
    }

    # connect to the CASH endpoint
    ep_cash  = BASE_URL + ENDPOINT_CASH

    # inform the user we are connecting
    print(" ")
    print(" ")
    print(f"Connecting to: {ep_cash}...")
    print(" ")

    # perform a GET request and store the response in a variable
    rsp_cash = requests.get(ep_cash, headers=headers)
    time.sleep(3)

    # check the response is 200 (status Code 200 means 'success')
    if rsp_cash.status_code == 200 :

        # print a success message
        print("Success! Connection Established.")
        print(" ")

        # parse the JSON data from the response
        data_cash = rsp_cash.json()

        # print the data to the console
        print(" ")
        print("--- Your Account Cash Data ---")
        print(data_cash)
        print(" ")
        print(" ")

    # if the response code is not 200, print an error message
    else:

        # return the status code
        print(f"Failed. Status Code: {rsp_cash.status_code}")
        print(" ")

        # return the reason for failure
        print(f"Reason: {rsp_cash.text}")
        print(" ")
        return

    ###########
    # HISTORY #
    ###########

    # connect to the HISTORY endpoint
    ep_hist = BASE_URL + ENDPOINT_HISTORY

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

    # request .csv reports
    print(f"Connecting to: {ep_hist}...")
    print(" ")

    # perform POST request on endpoint
    pstr = requests.post(ep_hist, json=payload, headers=headers)
    time.sleep(3)
    if pstr.status_code == 200:
      dpst = pstr.json()
      if dpst:
        rpt_id = dpst.get("reportId")
        print(f"Report ID: {rpt_id}")
        print(" ")
      else:
        print("No report id in the POST response")
        print(" ")
        return
    else:
      print(f"Failed. Status Code: {pstr.status_code}")
      print(" ")
      print(f"Reason: {pstr.text}")
      print(" ")
      return

    # set loop variable
    attempts = 10
    count = 1

    while count < attempts:
      print(f"Checking status, attempt {count} of {attempts}...")
      print(" ")
      getr = requests.get(ep_hist, headers = headers)
      if getr.status_code == 200:
        data_hist = getr.json()
        if data_hist and data_hist[0].get("status") == "Finished":
          print("Report has finished generating")
          dl_url = data_hist[0].get("downloadLink")
          print(f"Download link is: {dl_url}")
          print(" ")
          break
      else:
        print(f"Failed. Status Code: {getr.status_code}")
        print(" ")
        print(f"Reason: {getr.text}")
        print(" ")
      count += 1
      time.sleep(5)

    status = data_hist[0].get("status")
    if status != "Finished":
      print("No reports finished generating in time")
      print(" ")
      return
    else:
      print("Report was generated successfully!")
      print("Now requesting download...")
      print(" ")

    if dl_url:
      df = pd.read_csv(dl_url)
      time.sleep(10)
    else:
      print("No download link exists..")
      print(" ")
      return

    if not df.empty:
      df.to_csv('history_report.csv', index=False)
      print("Printing first 3 lines of dataframe..")
      print(" ")
      print(df.head(3))
      print(" ")
    else:
      print("Dataframe is empty")
      print(" ")
      return

    # END OF CODE
    return

#####################
# EXECUTION CONTROL #
#####################

# This line ensures the script runs only when executed directly (if the .py script is imported the __name__ variable will be just 'main' and not '__main__')
if __name__ == "__main__":
    fetch_account_cash()
