#!/usr/bin/env python3
# seneca id: rbhandari17@myseneca.ca
#seneca.no:143292233
import shutil
import argparse

def check_disk_usage(path="/"):
    """
    Checks disk usage on the given path.
    Returns:
        (used_percent, free_percent, is_low_space)
    """
    total, used, free = shutil.disk_usage(path)
    used_percent = (used / total) * 100
    free_percent = (free / total) * 100
    is_low_space = free_percent < 10  # Trigger if less than 10% free

    return used_percent, free_percent, is_low_space

def simulate_cleanup(dry_run=False):
    """
    Placeholder function to simulate cleanup actions.
    Replace with actual cleanup calls later.
    """
    # Example sizes freed in bytes (simulate)
    freed_recycle = 200 * 1024 * 1024  # 200 MB
    freed_cache = 150 * 1024 * 1024    # 150 MB
    freed_apt = 300 * 1024 * 1024      # 300 MB

    if dry_run:
        print(f"[Dry-run] Would free ~{freed_recycle // (1024*1024)} MB from Recycle Bin")
        print(f"[Dry-run] Would free ~{freed_cache // (1024*1024)} MB from Browser Cache")
        print(f"[Dry-run] Would free ~{freed_apt // (1024*1024)} MB from Old Packages")
        print("[Dry-run] No files actually deleted.")
        total_freed = 0
    else:
        # Here you would call the real cleanup functions and accumulate freed space.
        print(f"Freed {freed_recycle // (1024*1024)} MB from Recycle Bin")
        print(f"Freed {freed_cache // (1024*1024)} MB from Browser Cache")
        print(f"Freed {freed_apt // (1024*1024)} MB from Old Packages")
        total_freed = freed_recycle + freed_cache + freed_apt
        print(f"Total space freed: {total_freed // (1024*1024)} MB")

    return total_freed

def main():
    parser = argparse.ArgumentParser(description="Disk usage check and cleanup utility.")
    parser.add_argument('--force', '-f', action='store_true',
                        help='Force cleanup regardless of free space.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate cleanup without deleting files.')
    parser.add_argument('--threshold', type=int, default=10,
                        help='Free space percentage threshold to trigger cleanup (default: 10).')
    args = parser.parse_args()

    used, free, is_low = check_disk_usage()

    print(f"Disk usage: Used {used:.2f}% | Free {free:.2f}% (Threshold: {args.threshold}%)")

    # Decide if cleanup needed
    if free < args.threshold or args.force:
        if args.force and free >= args.threshold:
            print("Force flag used. Running cleanup regardless of free space.")
        else:
            print("Free space below threshold. Running cleanup.")
        simulate_cleanup(dry_run=args.dry_run)
    else:
        print("Sufficient free space. No cleanup needed.")
        if args.dry_run:
            print("[Dry-run] No actions performed.")

if __name__ == "__main__":
    main()
