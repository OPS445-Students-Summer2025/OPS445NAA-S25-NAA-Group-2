#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse
import pwd
import sys

def get_size(path):
    """Recursively calculate total size of files in the given path."""
    total_size = 0
    if not os.path.exists(path):
        return 0
    # If it's a file, return its size directly
    if os.path.isfile(path):
        return os.path.getsize(path)
    # If it's a directory, walk through it
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                # If file is inaccessible (permission or broken link), skip it
                continue
    return total_size

def empty_dir(path):
    """Delete all contents of the directory at the given path (but not the directory itself)."""
    if not os.path.isdir(path):
        return 0
    freed = 0
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        try:
            if os.path.islink(full_path) or os.path.isfile(full_path):
                # accumulate size for reporting
                freed += os.path.getsize(full_path) if os.path.exists(full_path) else 0
                os.remove(full_path)
            elif os.path.isdir(full_path):
                # if directory, calculate its size then remove it entirely
                freed += get_size(full_path)
                shutil.rmtree(full_path)
        except Exception as e:
            print(f"Warning: Could not remove {full_path}: {e}", file=sys.stderr)
    return freed

def main():
    # Set up argparse for command-line options
    parser = argparse.ArgumentParser(description="Disk cleanup utility for Ubuntu that frees space by clearing Trash, browser caches, and apt caches.")
    parser.add_argument("--threshold", type=int, default=10, help="Free space threshold (percentage) to trigger cleanup (default: 10%%)")
    parser.add_argument("--yes", "-y", action="store_true", help="Automatically confirm cleanup (no prompt).")
    parser.add_argument("--dry-run", action="store_true", help="Show what actions would be taken, without deleting or modifying anything.")
    args = parser.parse_args()

    # Root privilege check
    if os.geteuid() != 0:
        # In dry-run mode, we allow non-root to proceed with simulation (with limited scope)
        if not args.dry_run:
            print("Error: This script must be run as root (use sudo).")
            sys.exit(1)
        else:
            print("Warning: Running dry-run without root. Some checks may not have access to all files.", file=sys.stderr)

    # Determine which user's data to clean (in case of sudo, target the invoking user's Trash, caches)
    if "SUDO_USER" in os.environ and os.environ["SUDO_USER"]:
        target_user = os.environ["SUDO_USER"]
    else:
        # If not run via sudo, use current user
        target_user = os.environ.get("USER") or pwd.getpwuid(os.getuid()).pw_name

    try:
        user_info = pwd.getpwnam(target_user)
        user_home = user_info.pw_dir
    except KeyError:
        # Fallback: if user not found, use current $HOME or /root as last resort
        user_home = os.path.expanduser("~")

    # Paths to clean
    trash_dir = os.path.join(user_home, ".local", "share", "Trash")
    trash_files_dir = os.path.join(trash_dir, "files")
    trash_info_dir = os.path.join(trash_dir, "info")
    ff_cache1 = os.path.join(user_home, ".cache", "mozilla", "firefox")
    ff_cache2 = os.path.join(user_home, "snap", "firefox", "common", ".cache", "mozilla", "firefox")

    # Check disk usage on root filesystem
    usage = shutil.disk_usage("/")
    total_bytes = usage.total
    free_bytes = usage.free
    free_percent = (free_bytes / total_bytes) * 100 if total_bytes > 0 else 0.0

    # Display current disk free percentage
    print(f"Current free space: {free_percent:.2f}% (threshold: {args.threshold}%)")

    # If free space is below the threshold, we need to perform cleanup
    if free_percent < args.threshold:
        # If dry-run, print what would be done
        if args.dry_run:
            print(f"Free space is below {args.threshold}%. (Dry-run) The following actions would be taken:")
        else:
            print(f"Free space is below {args.threshold}%. Cleanup actions are required.")

        # List of actions that will be (or would be) performed
        actions = []
        if os.path.isdir(trash_dir):
            actions.append(f"Empty Trash at {trash_dir}")
        if os.path.isdir(ff_cache1):
            actions.append(f"Clear Firefox cache at {ff_cache1}")
        if os.path.isdir(ff_cache2):
            actions.append(f"Clear Firefox Snap cache at {ff_cache2}")
        actions.append("Remove unnecessary packages (apt-get autoremove)")
        actions.append("Clear apt cache (apt-get clean)")

        # Show planned actions and prompt for confirmation if not auto-confirmed
        if not args.yes:
            print("Planned cleanup actions:")
            for act in actions:
                print(f"  - {act}")
            # Prompt user for confirmation
            if args.dry_run:
                prompt = "Confirm simulation of these actions? [y/N]: "
            else:
                prompt = "Proceed with these actions? [y/N]: "
            try:
                response = input(prompt)
            except Exception:
                response = 'n'
            if response.strip().lower() not in ("y", "yes"):
                print("Cleanup canceled by user.")
                return  # Exit without performing actions
        else:
            # --yes provided, no prompt
            if args.dry_run:
                print("Dry-run mode: auto-confirming simulation of cleanup actions (--yes used).")
            else:
                print("Auto-confirming cleanup actions (--yes flag used).")

        # Perform (or simulate) the cleanup actions
        total_freed = 0
        # 1. Empty Trash contents
        if os.path.isdir(trash_dir):
            if args.dry_run:
                size = get_size(trash_dir)
                print(f"[Dry-run] Would empty Trash at {trash_dir} (recover ~{size//(1024*1024)} MB).")
            else:
                freed = 0
                # Empty 'files' and 'info' subdirectories if they exist
                freed += empty_dir(trash_files_dir)
                freed += empty_dir(trash_info_dir)
                print(f"Emptied Trash at {trash_dir}.")
                total_freed += freed
        else:
            print(f"No Trash directory found at {trash_dir}, skipping.")

        # 2. Clear Firefox cache (regular)
        if os.path.isdir(ff_cache1):
            if args.dry_run:
                size = get_size(ff_cache1)
                print(f"[Dry-run] Would clear Firefox cache at {ff_cache1} (recover ~{size//(1024*1024)} MB).")
            else:
                freed = get_size(ff_cache1)
                try:
                    shutil.rmtree(ff_cache1)
                except Exception as e:
                    print(f"Warning: Failed to remove {ff_cache1}: {e}", file=sys.stderr)
                else:
                    print(f"Cleared Firefox cache at {ff_cache1}.")
                total_freed += freed
        else:
            # If the directory doesn't exist, perhaps Firefox not installed or using Snap only
            print(f"No Firefox cache at {ff_cache1}, skipping.")

        # 3. Clear Firefox cache (Snap)
        if os.path.isdir(ff_cache2):
            if args.dry_run:
                size = get_size(ff_cache2)
                print(f"[Dry-run] Would clear Firefox Snap cache at {ff_cache2} (recover ~{size//(1024*1024)} MB).")
            else:
                freed = get_size(ff_cache2)
                try:
                    shutil.rmtree(ff_cache2)
                except Exception as e:
                    print(f"Warning: Failed to remove {ff_cache2}: {e}", file=sys.stderr)
                else:
                    print(f"Cleared Firefox Snap cache at {ff_cache2}.")
                total_freed += freed
        else:
            print(f"No Firefox Snap cache at {ff_cache2}, skipping.")

        # 4. Run apt-get autoremove and apt-get clean
        if args.dry_run:
            # In dry-run, don't actually run apt, just simulate
            # We can try to estimate apt cache size:
            cache_dir = "/var/cache/apt/archives"
            cache_size = get_size(cache_dir) if os.path.isdir(cache_dir) else 0
            print(f"[Dry-run] Would run 'apt-get autoremove' to remove unneeded packages.")
            print(f"[Dry-run] Would run 'apt-get clean' to clear APT cache (about {cache_size//(1024*1024)} MB in {cache_dir}).")
            # (Optionally, we could simulate apt autoremove by running apt-get -s, but skipping for dry-run.)
        else:
            # Run apt-get autoremove
            try:
                print("Running apt-get autoremove ...")
                # Use -y to auto-confirm removal of packages
                subprocess.run(["apt-get", "-y", "autoremove"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error: 'apt-get autoremove' failed (exit code {e.returncode}).", file=sys.stderr)
            # Run apt-get clean
            try:
                print("Running apt-get clean ...")
                subprocess.run(["apt-get", "clean"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error: 'apt-get clean' failed (exit code {e.returncode}).", file=sys.stderr)
            # After apt commands, calculate freed space on root partition
            new_free_bytes = shutil.disk_usage("/").free
            apt_freed = new_free_bytes - free_bytes  # difference after apt operations
            if apt_freed < 0:
                apt_freed = 0  # (in case something else consumed space, avoid negative)
            total_freed += apt_freed

        # Summarize results
        if args.dry_run:
            print("\n[Dry-run] Cleanup simulation completed.")
            # For dry-run, we estimated freed space in each step (sum sizes of targets) as total_freed
            # The total_freed in dry-run currently includes only Trash and Firefox parts.
            estimated_total = total_freed
            # If we have an estimate of apt cache, add it for total estimation
            if args.dry_run and os.path.isdir("/var/cache/apt/archives"):
                estimated_total += get_size("/var/cache/apt/archives")
            print(f"Estimated space that would be freed: ~{estimated_total//(1024*1024)} MB.")
        else:
            # Actual cleanup done
            # Recalculate free space after all actions
            final_usage = shutil.disk_usage("/")
            final_free_bytes = final_usage.free
            freed_mb = total_freed / (1024*1024)
            print("\nCleanup completed. Summary:")
            print(f"- Total space freed: ~{freed_mb:.2f} MB")
            # Show new free space percentage
            new_free_percent = (final_free_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
            print(f"- Free space before: {free_percent:.2f}% -> after: {new_free_percent:.2f}%")
            if total_freed > 0:
                print("Disk space has been successfully reclaimed.")
            else:
                print("No files were removed or no space was freed (system might have already been clean).")
    else:
        # If free space is above threshold, no action needed
        print(f"Free space is above the threshold of {args.threshold}%. No cleanup needed.")
        # Optionally, in dry-run mode, we can still list what would be done if it were below threshold.
        if args.dry_run:
            print("Dry-run: No cleanup actions would be taken as free space is sufficient.")

if __name__ == "__main__":
    main()
