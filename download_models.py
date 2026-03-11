#!/usr/bin/env python3
"""Download age estimation model files."""

import os
import urllib.request
import sys

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODELS = {
    "age_deploy.prototxt": [
        "https://raw.githubusercontent.com/tkim602/age-gender-prediction-opencv/main/AgeGender/age_deploy.prototxt",
    ],
    "age_net.caffemodel": [
        "https://raw.githubusercontent.com/tkim602/age-gender-prediction-opencv/main/AgeGender/age_net.caffemodel",
    ],
}


def download_file(url: str, dest: str) -> bool:
    """Download a file from URL to destination."""
    try:
        print(f"Downloading from {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            # Check if we got HTML instead of the file
            if b'<!DOCTYPE html>' in data[:100] or b'<html' in data[:100]:
                print("  Got HTML instead of file, trying next URL...")
                return False
            with open(dest, 'wb') as f:
                f.write(data)
            print(f"  Saved to {dest}")
            return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False


def main():
    """Download all model files."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    success = True
    for filename, urls in MODELS.items():
        dest = os.path.join(MODEL_DIR, filename)
        if os.path.exists(dest):
            print(f"{filename} already exists, skipping.")
            continue

        downloaded = False
        for url in urls:
            if download_file(url, dest):
                downloaded = True
                break

        if not downloaded:
            print(f"ERROR: Failed to download {filename}")
            success = False

    if success:
        print("\nAll models downloaded successfully!")
    else:
        print("\nSome models failed to download. Please download manually:")
        print("  - age_net.caffemodel")
        print("  - age_deploy.prototxt")
        print("\nPlace them in the models/ directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
