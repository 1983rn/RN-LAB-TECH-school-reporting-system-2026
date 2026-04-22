
import os
import glob

# Pattern for backup files in the root directory
pattern = "school_reports_backup_*.db"
files = glob.glob(pattern)

print(f"Found {len(files)} backup files.")

# Sort files by name (which includes timestamp)
files.sort()

# Keep the 3 most recent ones in the root, just in case
# The rest can be deleted
files_to_delete = files[:-3]
files_to_keep = files[-3:]

print(f"Keeping: {files_to_keep}")
print(f"Deleting {len(files_to_delete)} files...")

deleted_count = 0
for f in files_to_delete:
    try:
        os.remove(f)
        deleted_count += 1
    except Exception as e:
        print(f"Error deleting {f}: {e}")

print(f"\nSuccessfully deleted {deleted_count} files.")
