#!/usr/bin/env python3
"""Setup Telegram webhook to Vercel. Run once."""

import os
import sys
import urllib.request

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = "https://dashboard-jade-pi-57.vercel.app/api/telegram"

if not BOT_TOKEN:
    BOT_TOKEN = input("Enter Telegram Bot Token: ").strip()

if not BOT_TOKEN:
    print("ERROR: No token provided")
    sys.exit(1)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
resp = urllib.request.urlopen(url)
print(resp.read().decode())
print(f"\nWebhook set to: {WEBHOOK_URL}")
print("Now send /start to your bot on Telegram!")
