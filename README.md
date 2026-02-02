Overview
Build a command-line tool to organize messy folders, find duplicate files, and perform bulk file operations.

Core Requirements

1. Organize Files by Type
    • Scan a directory for files 
    • Create category folders (Images, Documents, Audio, Videos, Archives, Others) 
    • Move files to appropriate folders based on extension 
    • Handle filename conflicts safely 
    • Show statistics after organizing 
Example Command:
python organizer.py organize ~/Downloads
Expected Output:
📂 Organizing ~/Downloads...

Created folders:
  📷 Images/     (45 files)
  📄 Documents/  (23 files)
  🎵 Audio/      (12 files)
  🎬 Videos/     (8 files)
  📦 Archives/   (5 files)
  ❓ Others/     (3 files)

Organized 96 files in 3.2 seconds

2. Find Duplicate Files
    • Scan directory recursively 
    • Use file hashing (MD5 or SHA-256) to detect duplicates 
    • Compare by content, not filename 
    • Group duplicates together 
    • Show size and total wasted space 
    • Option to delete duplicates (keep one copy) 
Example Commands:
python organizer.py duplicates ~/Documents --scan
python organizer.py duplicates ~/Documents --remove

3. Bulk Rename Files
    • Rename multiple files using patterns 
    • Add prefix or suffix to filenames 
    • Use counters in filenames 
    • Add dates to filenames 
    • Preview changes before applying 
Example Commands:
python organizer.py rename ~/Photos --pattern "vacation_{count}.jpg"
python organizer.py rename ~/Photos --add-prefix "2024_"
python organizer.py rename ~/Photos --add-date

4. Find Large Files
    • Search for files above a size threshold 
    • Sort by size (largest first) 
    • Show file path and size in human-readable format (KB, MB, GB) 
    • Calculate total size of large files 
Example Command:
python organizer.py find-large ~/Documents --min-size 100MB

5. Clean Up Old Files
    • Find files older than specified days 
    • Show total size of old files 
    • Option to delete with confirmation 
    • Find and remove empty folders 
Example Commands:
python organizer.py cleanup ~/Downloads --older-than 30
python organizer.py cleanup ~/Downloads --empty-folders

6. Generate Directory Tree
    • Display folder structure as a tree 
    • Limit depth of traversal 
    • Show file sizes 
    • Calculate total files and size 
Example Command:
python organizer.py tree ~/Projects --depth 2

------------------------------------------------------------------------------------------------------------------------

Configuration File

config.json:
{
  "categories": {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".odt"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp"]
  },
  "ignore": [".DS_Store", "Thumbs.db", ".git", "__pycache__"]
}

Required Modules
    • os - file system operations 
    • shutil - moving and copying files 
    • hashlib - file hashing for duplicate detection 
    • json - configuration file handling 
    • pathlib - modern path handling (optional, can use os.path) 
    • datetime - file age checking 
    • sys or argparse - command-line arguments 