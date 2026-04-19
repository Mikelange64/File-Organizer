# File Organizer

A command-line tool for organizing, cleaning, and managing files on your system. Supports sorting files by type, finding and removing duplicates, bulk renaming, locating large files, cleaning up old or empty folders, and undoing any previous operation.

## Features

- **Organize** — Sort files into categorized subfolders (Documents, Images, Videos, Audios, Archives, Others)
- **Duplicate detection** — Find duplicate files using MD5 hashing; choose which to keep or delete
- **Bulk rename** — Rename files using custom patterns, or add prefixes, suffixes, and dates
- **Find large files** — Locate files above a size threshold, with optional recursive search
- **Clean up** — Delete files older than N days or remove empty folders
- **Directory tree** — Display a visual tree of any directory
- **Undo** — Reverse the last operation (move, rename, or delete with backup restore)

## Requirements

- Python 3.10+

No third-party packages required — uses only the Python standard library.

## Installation

```bash
git clone https://github.com/Mikelange64/File-Organizer.git
cd File-Organizer/src
```

## Usage

Run from the `src/` directory:

```bash
python file_organizer.py <command> [options]
```

### Commands

#### `organize` — Sort files into subfolders by type

```bash
python file_organizer.py organize ~/Downloads
```

Creates subfolders: `Documents/`, `Images/`, `Videos/`, `Audios/`, `Archives/`, `Others/`

---

#### `duplicate` — Find (and optionally delete) duplicate files

```bash
# Find duplicates larger than 500KB
python file_organizer.py duplicate ~/Downloads --min-size 500KB

# Include system directories and virtual environments
python file_organizer.py duplicate ~/Projects --all
```

Uses MD5 hashing to identify exact duplicates. Automatically excludes `.git`, `node_modules`, `__pycache__`, and other build/system directories by default.

---

#### `rename` — Bulk rename files

**Using a pattern** (placeholders: `{name}`, `{count}`, `{doc_type}`, `{last_modified}`):

```bash
python file_organizer.py rename ~/Photos --pattern "{last_modified}_{count}"
```

**Using prefix / suffix / date:**

```bash
python file_organizer.py rename ~/Reports --add-prefix "2025" --add-suffix "final"
python file_organizer.py rename ~/Reports --add-date 2025-01-01
```

---

#### `find-large` — List files above a size threshold

```bash
python file_organizer.py find-large ~/Downloads --min-size 100MB
python file_organizer.py find-large ~/Projects --min-size 50MB --recursive
```

---

#### `clean-up` — Delete old files or empty folders

```bash
# Delete files not modified in over 90 days
python file_organizer.py clean-up ~/Downloads --older-than 90

# Remove empty folders
python file_organizer.py clean-up ~/Projects --empty-folder

# Search recursively
python file_organizer.py clean-up ~/Projects --older-than 180 --recursive
```

Files are backed up before deletion, allowing recovery via `undo`.

---

#### `tree` — View directory structure

```bash
python file_organizer.py tree ~/Projects
python file_organizer.py tree ~/Projects --depth 2
```

---

#### `undo` — Reverse the last operation

```bash
python file_organizer.py undo
```

Supports undoing: organize (moves files back), rename (restores original names), and delete (restores backed-up files from `.last_deleted/`).

## Project Structure

```
File Organizer/
├── src/
│   ├── file_organizer.py   # Main CLI tool
│   └── fileExtensions.py   # File type extension mappings
├── tests/
│   └── test_organizer.py   # Pytest test suite
├── Gemini version/          # Alternative implementation (AI-assisted comparison)
└── .operations.json         # Auto-generated operation log for undo support
```

## Running Tests

```bash
pip install pytest
pytest tests/
```
