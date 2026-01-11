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

    # add the api_key to a variable for use in the function
    key_id, secret_key = get_api_key()

    # exit the function if we didn't get a key
    if not key_id or not secret_key:
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
    print(f"Connecting to: {ep_cash}...")

    # perform a GET request and store the response in a variable
    rsp_cash = requests.get(ep_cash, headers=headers)

    # check the response is 200 (status Code 200 means 'success')
    if rsp_cash.status_code == 200 :

        # print a success message
        print("Success! Connection Established.")

        # parse the JSON data from the response
        data_cash = rsp_cash.json()

        # print the data to the console
        print(" ")
        print("--- Your Account Cash Data ---")
        print(data_cash)
        print(" ")

    # if the response code is not 200, print an error message
    else:

        # return the status code
        print(f"Failed. Status Code: {rsp_cash.status_code}")

        # return the reason for failure
        print(f"Reason: {rsp_cash.text}")


    # connect to the HISTORY endpoint
    ep_hist = BASE_URL + ENDPOINT_HISTORY

    # request .csv reports
    print(f"Connecting to: {ep_hist}...")

    # perform GET request on endpoint
    rsp_hist = requests.get(ep_hist, headers=headers)

    # check the response code
    if rsp_hist.status_code == 200:

        # print success message
        print("Success! Connection estblished.")

        # parse the JSON data from the response
        data_hist = rsp_hist.json()

        # print data to the console
        print(" ")
        print("--- Response from History call ---")
        print(data_hist)
        print(" ")

    else:

        # return the status code
        print(f"Failed. Status Code: {rsp_hist.status_code}")

        # return the reason for failure
        print(f"Reason: {rsp_hist.text}")


#####################
# EXECUTION CONTROL #
#####################

# This line ensures the script runs only when executed directly (if the .py script is imported the __name__ variable will be just 'main' and not '__main__')
if __name__ == "__main__":
    fetch_account_cash()
