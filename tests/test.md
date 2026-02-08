1. Organize Files by Type (passed)

# Organize
python3 'file organizer.py' organize ~/Downloads

------------------------------------------------------------------------------------------------------------------------------------------------------------

2. Find Duplicate Files (passed)

# Scan for duplicates
python3 'file organizer.py' duplicate ~/Documents 

------------------------------------------------------------------------------------------------------------------------------------------------------------

3. Bulk Rename Files (passed)

# Rename using a pattern
python3 'file organizer.py' rename ~/Pictures/'Baby Pictures' --pattern "Baby pictures_{count}.jpg"

# Add a prefix
python3 'file organizer.py' rename ~/Photos --add-prefix "2024_"

# Add a suffix
python3 'file organizer.py' rename ~/Photos --add-suffix "_edited"

# Add a date
python3 'file organizer.py' rename ~/Photos --add-date "2025-02-06"

------------------------------------------------------------------------------------------------------------------------------------------------------------

4. Find Large Files (passed)

# Find files larger than 100 MB (non-recursive)
python3 'file organizer.py' find-large ~/Documents --min-size "100MB"

# Recursive search
python3 'file organizer.py' find-large ~/Documents --min-size "100MB" --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

5. Clean Up Old Files / Empty Folders (passed)

# Find files older than 30 days
python3 'file organizer.py' clean-up ~/Downloads --older-than 30

# Find empty folders (non-recursive)
python3 'file organizer.py' clean-up ~/Downloads --empty-folder

# Recursive cleanup
python3 'file organizer.py' clean-up ~/Downloads --empty-folder --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

6. Generate Directory Tree (passed)

# Tree with depth = 2
python3 'file organizer.py' tree ~/Projects --depth 2

# Unlimited depth (if you change parser to make --depth optional)
python3 'file organizer.py' tree ~/Projects

