"""
---------------------------------------------------------------------------------------------------------------------
Download files from Google Drive
---------------------------------------------------------------------------------------------------------------------
"""

___author__ = "Gowtham Bavireddy"

# import the required libraries
import argparse
import pickle
import os.path
import io
import shutil
import sys
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
global SCOPES_API


class DriveAPI:
    # Define the scopes
    SCOPES_API = ['https://www.googleapis.com/auth/drive']

    def __init__(self, credentials_path=None):

        # Variable self.creds will
        # store the user access token.

        self.creds = credentials_path

        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.

        # Check if file token.pickle exists
        if os.path.exists('token.pickle'):
            # Read the token from the file and
            # store it in the variable self.creds
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials are available,
        # request the user to log in.
        if not self.creds or not self.creds.valid:

            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds, SCOPES_API)
                self.creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle
            # file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)

        # request a list of first N files or
        # folders with name and id from the API.
        results = self.service.files().list(
            pageSize=100, fields="files(id, name)").execute()
        items = results.get('files', [])

        # logging.info a list of files

        logging.info("Here's a list of files: \n")
        for i in items:
            logging.info(i)

    def file_download(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)

            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)

            logging.info("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except HttpError as error:
            # Return False if something went wrong
            logging.error(f'An error occurred: {error}')
            return False


if __name__ == "__main__":
    # Set up argument parser ---------------------------------------------------------------------------------------
    arg_parser = argparse.ArgumentParser(description="Parser for the Google Drive Download parameters",
                                         prog=sys.argv[0])
    # add arguments that can appear in the command line
    arg_parser.add_argument("-credentials", "-credentials_path", dest="credentials_path", type=str, required=True,
                            help="Full path to the google drive URL.")
    arg_parser.add_argument("-file_id", "-file_id", dest="file_id", type=str, required=True,
                            help="ID of the file")
    arg_parser.add_argument("-file_name", "-file_name", dest="file_name", type=str, required=True,
                            help="Name of the file")
    arguments = arg_parser.parse_args()  # Parse command line arguments

    drive_obj = DriveAPI(credentials_path=arguments.credentials_path)
    drive_obj.file_download(file_id=arguments.file_id, file_name=arguments.file_name)
