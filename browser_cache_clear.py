#!/usr/bin/env python3
"""Clears browser cache for Firefox and Chromium (Linux only)."""

import os
import shutil

def clear_cache():
    browsers = {
        "Firefox": os.path.expanduser("~/.cache/mozilla/firefox"),
        "Chromium": os.path.expanduser("~/.cache/chromium")
    }

    for name, path in browsers.items():
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"{name} cache cleared.")
            except Exception as e:
                print(f"Error clearing {name} cache: {e}")
        else:
            print(f"{name} cache not found.")
