from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from github import Github

SPREADSHEET_ID = '1fcQR4xhy-J2XH1LOdPm-APfm5B-ulkAfbYoqVL7NhGA'
NAME_RANGE = 'RepoURL_Mobile'
STARS_RANGE = 'Stars_Mobile'
SIZE_RANGE = 'Size_Mobile'
COUNT_RANGE = 'Count_Mobile'
GITHUB_TOKEN = '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'
INPUT_OPTION = "USER_ENTERED"


def update_stars(g, service, spreadsheet_id, url_range, stars_range):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=url_range).execute()
    stars = []
    values = result.get('values', [])

    for row in values:
        url = row[0]
        name = url[len('https://github.com/'):]
        try:
            repo = g.get_repo(name)
            stars.append([str(repo.stargazers_count)])
        except:
            stars.append([""])
            print("invalid url: " + url)
    body = {
        'values': stars
    }
    sheet.values().update(spreadsheetId=spreadsheet_id, range=stars_range,
                          valueInputOption=INPUT_OPTION, body=body).execute()


def update_contributor_count(g, service, spreadsheet_id, url_range, count_range):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=url_range).execute()
    counts = []
    values = result.get('values', [])
    for row in values:
        url = row[0]
        name = url[len('https://github.com/'):]
        try:
            repo = g.get_repo(name)
            counts.append([str(repo.get_contributors().totalCount)])
        except:
            counts.append([""])
            print("invalid url: " + url)
    body = {
        'values': counts
    }
    sheet.values().update(spreadsheetId=spreadsheet_id, range=count_range,
                          valueInputOption=INPUT_OPTION, body=body).execute()


def update_size(g, service, spreadsheet_id, url_range, sizes_range):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=url_range).execute()
    sizes = []
    values = result.get('values', [])
    for row in values:
        url = row[0]
        name = url[len('https://github.com/'):]
        try:
            repo = g.get_repo(name)
            sizes.append([str(repo.size)])
        except:
            sizes.append([""])
            print("invalid url: " + url)
    body = {
        'values': sizes
    }
    sheet.values().update(spreadsheetId=spreadsheet_id, range=sizes_range,
                          valueInputOption=INPUT_OPTION, body=body).execute()


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
    # sheet.values().update(spreadsheetId=spreadsheet_id, range=keyword_range,
    #                       valueInputOption=INPUT_OPTION, body=body).execute()


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
    g = Github(GITHUB_TOKEN)
    # update_stars(g, service, SPREADSHEET_ID, NAME_RANGE, STARS_RANGE)
    # update_contributor_count(
    #     g, service, SPREADSHEET_ID, NAME_RANGE, COUNT_RANGE)
    # update_size(g, service, SPREADSHEET_ID,
    #             NAME_RANGE, SIZE_RANGE)
    # update_stars(g, service, SPREADSHEET_ID,
    #              "RepoURL_Web", "Stars_Web")
    # update_contributor_count(
    #     g, service, SPREADSHEET_ID, "RepoURL_Web", "Count_Web")
    # update_size(g, service, SPREADSHEET_ID,
    #             "RepoURL_Web", "Size_Web")
    check_readme(g, service, SPREADSHEET_ID,
                 "RepoURL_Mobile", "Keywords_Mobile")
    check_readme(g, service, SPREADSHEET_ID, "RepoURL_Desktop", "Keywords_Desktop")
    check_readme(g, service, SPREADSHEET_ID, "RepoURL_Web", "Keywords_Web")


if __name__ == '__main__':
    main()
