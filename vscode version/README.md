# File Organizer & Duplicate Finder

Simple command-line tool to organize files, find duplicates, bulk rename, locate large files, clean up old files, and display directory trees.

Quick examples:

- Organize a folder:
```
python organizer.py organize ~/Downloads
```
- Find duplicates (preview):
```
python organizer.py duplicates ~/Documents
```
- Remove duplicates (keep first):
```
python organizer.py duplicates ~/Documents --remove
```
- Bulk rename with pattern:
```
python organizer.py rename ~/Photos --pattern "vacation_{count}.jpg" --preview
```
- Find large files (>=100MB):
```
python organizer.py find-large ~/Documents --min-size 100MB
```
- Cleanup files older than 30 days:
```
python organizer.py cleanup ~/Downloads --older-than 30
```
- Show directory tree depth 2:
```
python organizer.py tree ~/Projects --depth 2
```

Undo last move operation:
```
python organizer.py undo
```

Configuration is in `config.json`.
