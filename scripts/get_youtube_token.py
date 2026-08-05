#!/usr/bin/env python3
"""Get YouTube OAuth refresh token. Run this once locally."""

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CREDENTIALS_FILE = "client_secret.json"

if __name__ == "__main__":
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        print("Download it from Google Cloud Console → Credentials → OAuth 2.0 Client IDs")
        print("Save it as client_secret.json in this directory")
        exit(1)

    print("Starting OAuth flow...")
    print("A browser window will open. Log in with your YouTube Google account.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    print()
    print("=" * 60)
    print("SUCCESS! Copy this refresh token:")
    print("=" * 60)
    print(credentials.refresh_token)
    print("=" * 60)
    print()
    print("Now add it to GitHub Secrets:")
    print("  Settings → Secrets and variables → Actions → New repository secret")
    print("  Name: YOUTUBE_REFRESH_TOKEN")
    print(f"  Value: {credentials.refresh_token}")
