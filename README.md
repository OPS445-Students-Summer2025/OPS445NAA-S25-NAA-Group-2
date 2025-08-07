# Winter 2025 Assignment 2
# Disk Cleanup Project - OPS445 Group Assignment

This is a Python-based disk cleanup tool developed as a group project for OPS445. It performs essential cleanup tasks when disk space is low, including:

- Checking disk usage
- Emptying the recycle bin
- Clearing browser cache (Firefox/Chromium)
- Removing old APT packages
- Providing a cleanup summary

#Project Structure

| File | Description |
|------|-------------|
| `check_disk.py` | Checks if free disk space is below 10% |
| `clear_recycle_bin.py` | Deletes all files in the user's trash |
| `clear_browser_cache.py` | Deletes browser cache files (Linux only) |
| `clean_old_apt.py` | Runs `apt-get autoremove` to clean old packages |
| `summary.py` | Main script to coordinate and report all cleanup steps |

#How It Works

1. Run `summary.py`
2. It checks if disk space is low
3. If space is below 10%, it runs all cleanup modules
4. A final report is printed showing what was done

#Example Output

```
Starting disk cleanup...

Total: 120 GB, Used: 110 GB, Free: 10 GB (8.33%)
Low disk space: True

Running cleanup tasks...

Deleted: /home/user/.local/share/Trash/files/old_file.txt
Recycle bin cleared.
Firefox cache cleared.
Chromium cache cleared.
APT cleanup complete.

Cleanup Summary:
- recycle bin: Completed
- browser cache: Completed
- APT cleanup: Completed
```

#Contributors

- JunLong Wang - Summary feature & integration
- Rojina Bhandari - Disk check logic
- Urmil Rohitkumar Patel - Recycle bin cleanup
- Md Taki Yasir Faraji Sadik - Browser cache logic
- JunLong Wang - APT cleanup

#License

This project is for academic purposes (Seneca College - OPS445).
