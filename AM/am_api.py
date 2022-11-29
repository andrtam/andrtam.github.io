"""Account management API."""
from __future__ import print_function
from fastapi import FastAPI
import uvicorn
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service_key.json'

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '1tC__fhMbjkIjdLMmUeQj_kqlpymJ84v0oA8GH5nJvL0'


def append_values(spreadsheet_id, range_name, value_input_option, values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.

    Let there be no mistake, I copy pasted this.
    """
    try:
        service = build('sheets', 'v4', credentials=creds)

        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body, insertDataOption='INSERT_ROWS').execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def read_values(speadsheet_id: str, range: str):
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    username_to_password_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()
    values = username_to_password_data.get('values', [])
    return values


app = FastAPI()
data = ()

@app.post('/create_account')
def store_new_accaunt(forename, surname, day_of_birth, email, username, password):
    data = [[forename, surname, day_of_birth, email, username, password]]
    append_values('1tC__fhMbjkIjdLMmUeQj_kqlpymJ84v0oA8GH5nJvL0', 'Accounts!A1:F1', 'RAW', data)


@app.get('/is_account_valid')
def chack_validity(username, password):
    values = read_values(SPREADSHEET_ID, 'Accounts!E:F')
    if values:
        for row in values:
            if row[0] == username and row[1] == password:
                print(True)
                return True
    return False



@app.get('/existing_accounts')
def get_all_account_data():
    values = read_values(SPREADSHEET_ID, 'Accounts!A:F')
    return values


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
