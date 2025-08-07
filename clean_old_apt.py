#!/usr/bin/env python3
"""
Runs apt autoremove to clean old packages.
"""

import os

def clean_apt():
    print("Cleaning up old APT packages.")
    result = os.system("sudo apt-get autoremove -y")
    if result == 0:
        print("APT cleanup complete.")
    else:
        print("APT cleanup failed.")
