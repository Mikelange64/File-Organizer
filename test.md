# Organize Files by Type

1. Organize
python3 'file organizer.py' organize ~/Downloads

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Find Duplicate Files (passed)

2. Scan for duplicates
python3 'file organizer.py' duplicate ~/Documents 

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Bulk Rename Files (passed)

4. Rename using a pattern
python3 'file organizer.py' rename ~/Pictures/'Baby Pictures' --pattern "Baby pictures_{count}.jpg"

5. Add a prefix
python3 'file organizer.py' rename ~/Photos --add-prefix "2024_"

6. Add a suffix
python3 'file organizer.py' rename ~/Photos --add-suffix "_edited"

7. Add a date
python3 'file organizer.py' rename ~/Photos --add-date "2025-02-06"

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Find Large Files (passed)

8. Find files larger than 100 MB (non-recursive)
python3 'file organizer.py' find-large ~/Documents --min-size "100MB"

9. Recursive search
python3 'file organizer.py' find-large ~/Documents --min-size "100MB" --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Clean Up Old Files / Empty Folders (passed)

10. Find files older than 30 days
python3 'file organizer.py' clean-up ~/Downloads --older-than 30

11. Find empty folders (non-recursive)
python3 'file organizer.py' clean-up ~/Downloads --empty-folder

12. Recursive cleanup
python3 'file organizer.py' clean-up ~/Downloads --empty-folder --recursive

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Generate Directory Tree (passed)

13. Tree with depth = 2
python3 'file organizer.py' tree ~/Projects --depth 2

14. Unlimited depth (if you change parser to make --depth optional)
python3 'file organizer.py' tree ~/Projects

