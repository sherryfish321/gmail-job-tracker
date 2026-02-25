"""
gmail/auth.py
Google OAuth 2.0 authentication for Gmail API.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import (
    GMAIL_CREDENTIALS_PATH,
    GMAIL_OAUTH_PORT,
    GMAIL_SCOPES,
    GMAIL_TOKEN_PATH,
)


def get_service(
    credentials_path=GMAIL_CREDENTIALS_PATH,
    token_path=GMAIL_TOKEN_PATH,
):
    """
    Authenticate and return a Gmail API service object.
    First run will open browser for OAuth. Subsequent runs use cached token.
    """
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=GMAIL_OAUTH_PORT)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
