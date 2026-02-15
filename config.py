import os
from typing import Tuple, Optional

def get_api_keys(provider: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the API key and secret from the .env file.
    """
    api_key, api_secret = None, None
    try:
        # Determine the absolute path to the .env file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, ".env")
        
        # Check the requested provider
        if provider == "Trading212":
            # load data from the .env file into variables
            with open(env_path, "r") as file:
                for line in file:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        if parts[0] == "T212_API_KEY":
                            api_key = parts[1]
                        elif parts[0] == "T212_API_SECRET":
                            api_secret = parts[1]
            return api_key, api_secret
    except FileNotFoundError:
        print(f"\nError: .env file not found at {env_path}!")
        return None, None
    return None, None
