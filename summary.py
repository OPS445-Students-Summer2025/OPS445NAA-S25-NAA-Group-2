#!/usr/bin/env python3
"""
Summary script that uses all modules to achive disk cleanup feature.
"""

import check_disk
import cleanup
import browser_cache_clear
import clean_old_apt

def summary_report(actions_taken):
    report = "Cleanup Summary:\n"
    for action, taken in actions_taken.items():
        if taken:
            report += "- {}: Completed\n".format(action)
        else:
            report += "- {}: Skipped\n".format(action)
    return report

def main():
    print("Starting disk cleanup.\n")

    actions = {
        "recycle bin": False,
        "browser cache": False,
        "APT cleanup": False
    }

    low_space = check_disk.check_disk_usage()
    print("Low disk space:", low_space)

    if low_space:
        print("\nRunning cleanup tasks...\n")

        cleanup.main()
        actions["Recycle Bin"] = True

        browser_cache_clear.clear_cache()
        actions["Browser Cache"] = True

        clean_old_apt.clean_apt()
        actions["APT Cleanup"] = True
    else:
        print("\nDisk space is sufficient; no cleanup needed.")

    print("\n" + summary_report(actions))

if __name__ == "__main__":
    main()
