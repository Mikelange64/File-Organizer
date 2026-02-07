1. Organize Files by Type

# Organize
python3 'File Organizer.py' organize ~/Downloads

------------------------------------------------------------------------------------------------------------------------------------------------------------

2. Find Duplicate Files

# Scan for duplicates
python3 'File Organizer.py' duplicate ~/Documents --scan

------------------------------------------------------------------------------------------------------------------------------------------------------------

3. Bulk Rename Files

# Rename using a pattern
python3 'File Organizer.py' rename ~/Photos --pattern "vacation_{count}.jpg"

# Add a prefix
python3 'File Organizer.py' rename ~/Photos --add-prefix "2024_"

# Add a suffix
python3 'File Organizer.py' rename ~/Photos --add-suffix "_edited"

# Add a date
python3 'File Organizer.py' rename ~/Photos --add-date "2025-02-06"

------------------------------------------------------------------------------------------------------------------------------------------------------------

4. Find Large Files

# Find files larger than 100 MB (non-recursive)
python3 'File Organizer.py' find-large ~/Documents --min-size "100MB"

# Recursive search
python3 'File Organizer.py' find-large ~/Documents --min-size "100MB" --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

5. Clean Up Old Files / Empty Folders

# Find files older than 30 days
python3 'File Organizer.py' clean-up ~/Downloads --older-than 30

# Find empty folders (non-recursive)
python3 'File Organizer.py' clean-up ~/Downloads --empty-folder

# Recursive cleanup
python3 'File Organizer.py' clean-up ~/Downloads --empty-folder --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

6. Generate Directory Tree

# Tree with depth = 2
python3 'File Organizer.py' tree ~/Projects --depth 2

# Unlimited depth (if you change parser to make --depth optional)
python3 'File Organizer.py' tree ~/Projects

