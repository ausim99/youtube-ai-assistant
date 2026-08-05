#!/usr/bin/env python3
"""Setup script for YouTube AI Assistant."""

import os
import sys


def create_env_file():
    """Create .env file from .env.example if not exists."""
    if os.path.exists(".env"):
        print(".env file already exists. Skipping.")
        return

    if os.path.exists(".env.example"):
        with open(".env.example") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print("Created .env file from .env.example")
    else:
        print("No .env.example found. Please create .env manually.")


def create_dirs():
    """Create required directories."""
    dirs = [
        "backend/storage/logs",
        "backend/storage/videos",
        "backend/storage/audio",
        "backend/storage/images",
        "backend/storage/thumbnails",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")


def main():
    print("=" * 50)
    print("YouTube AI Assistant - Setup")
    print("=" * 50)

    create_dirs()
    create_env_file()

    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start backend: cd backend && uvicorn main:app --reload")
    print("4. Start dashboard: cd dashboard && npm install && npm run dev")
    print("\nOr use Docker: docker compose up")


if __name__ == "__main__":
    main()
