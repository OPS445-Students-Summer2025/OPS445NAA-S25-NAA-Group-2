#!/usr/bin/env python3

import os
import shutil
import pwd
import sys

def get_user_home():
    """Returns the home directory of the user who invoked sudo, or the current user."""
    if "SUDO_USER" in os.environ and os.environ["SUDO_USER"]:
        target_user = os.environ["SUDO_USER"]
    else:
        target_user = os.environ.get("USER") or pwd.getpwuid(os.getuid()).pw_name

    try:
        return pwd.getpwnam(target_user).pw_dir
    except KeyError:
        return os.path.expanduser("~")

def get_size(path):
    """Returns total size of all files under a directory or single file."""
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                continue
    return total

def empty_trash(trash_path):
    """Empties the Trash directory contents (files and info subfolders)."""
    if not os.path.isdir(trash_path):
        print(f"No Trash directory found at: {trash_path}")
        return 0

    total_freed = 0
    for item in os.listdir(trash_path):
        item_path = os.path.join(trash_path, item)
        try:
            item_size = get_size(item_path)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
            total_freed += item_size
        except Exception as e:
            print(f"Could not remove {item_path}: {e}", file=sys.stderr)
    
    return total_freed

def main():
    user_home = get_user_home()
    trash_dir = os.path.join(user_home, ".local", "share", "Trash")
    trash_files = os.path.join(trash_dir, "files")
    trash_info = os.path.join(trash_dir, "info")

    print(f"Cleaning Trash for user: {user_home}")
    freed_files = empty_trash(trash_files)
    freed_info = empty_trash(trash_info)
    total = (freed_files + freed_info) // (1024 * 1024)

    print(f"Recycle Bin cleanup complete. Freed ~{total} MB.")

if __name__ == "__main__":
    main()

