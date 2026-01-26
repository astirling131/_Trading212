########################################################
#
# Name: Run.py
# Author: Andrew Stirling
# Version: 1.01
# Description: Install python dependancies and
#              import main.py to start program
#
########################################################

import sys
import subprocess
import os

def install_dependencies():

    # get requirements from text file
    req_file = "requirements.txt"

    # exit script if no requirements file exists
    if not os.path.exists(req_file):
        print("No requirements.txt found. Skipping install.")
        sys.exit(1)

    # install dependancies
    print("\nChecking dependencies...")
    try:
        # Run the pip install command (system agnostic)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("Dependencies OK\n")
    except subprocess.CalledProcessError as e:
        print(f"\nError installing dependencies: {e}")
        sys.exit(1)


##################
# MAIN EXECUTION #
##################

if __name__ == "__main__":

    # install python dependancies
    install_dependencies()

    # import main python script
    try:
        import main
        print(f"Launching app...\n")
        # launch app function
        main.launch_app()
    except ImportError as e:
        # warn user on error
        print(f"Critical Import Error: {e}\n")
