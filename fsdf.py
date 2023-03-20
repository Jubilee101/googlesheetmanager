from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from github import Github

SPREADSHEET_ID = '1vMQYHcVIx4ewd5gXHwVmY5thNCeiwsg8YfXwJ2ri1c4'
NAME_RANGE = 'RepoURL_Mobile'
STARS_RANGE = 'Stars_Mobile'
SIZE_RANGE = 'Size_Mobile'
COUNT_RANGE = 'Count_Mobile'
GITHUB_TOKEN = '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'
INPUT_OPTION = "USER_ENTERED"
SHEETS = []

def get_data(service, sheet):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet, range='poseosc').execute()
    values = result.get('values', [])
    for row in values: 
        for cell in row:
            print(cell)
    

def check_readme(g, service, spreadsheet_id, url_range, keyword_range):
    keywords = ["Fairness", "Reliability", "Safety", "Privacy", "Security", "Inclusiveness", "Transparency", "Accountability",
                "Explainability", "Robustness", "Governance", "Policy", "Ethics", "Ethical AI", "Responsible AI", "Trustworthy AI"]
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=url_range).execute()
    checked = []
    values = result.get('values', [])
    for row in values:
        url = row[0]
        name = url[len('https://github.com/'):]
        word_list = ""
        try:
            repo = g.get_repo(name)
            contents = repo.get_contents("README.txt")
            text = str(contents.decoded_content)
            for word in keywords:
                if word.lower() in text.lower():
                    word_list = word_list + word + " "
            checked.append([word_list])
        except Exception as e:
            checked.append([])
            print("url: " + url)
            print(e)
    body = {
        'values': checked
    }



def main():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('sheets', 'v4', credentials=creds)
    get_data(service, SPREADSHEET_ID)


if __name__ == '__main__':
    main()
