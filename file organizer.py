from argparse import ArgumentParser
from pathlib import Path
import shutil
import re
import hashlib
from datetime import datetime as dt, timedelta
import time
from collections import defaultdict
import logging
import fileExtensions

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)


class FileOrganizer:

    @staticmethod
    def organize_dir(args):
        logging.info(f'Starting organize_dir with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        logging.debug('Creating category folders')
        (directory/'Documents').mkdir(exist_ok=True, parents=True)
        (directory/'Images').mkdir(exist_ok=True, parents=True)
        (directory/'Videos').mkdir(exist_ok=True, parents=True)
        (directory/'Audios').mkdir(exist_ok=True, parents=True)
        (directory/'Archives').mkdir(exist_ok=True, parents=True)
        (directory/'Others').mkdir(exist_ok=True, parents=True)
        logging.debug('Category folders created successfully')

        doc_count = 0
        img_count = 0
        vid_count = 0
        aud_count = 0
        arc_count = 0
        other_count = 0

        start_time = time.perf_counter()
        logging.info('Starting file organization process')

        for item in list(directory.iterdir()):

            if not item.is_file():
                continue

            suffix_lower = item.suffix.lower()

            if suffix_lower in fileExtensions.document_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Documents'/item.name)
                doc_count += 1

            elif suffix_lower in fileExtensions.image_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Images'/item.name)
                img_count += 1

            elif suffix_lower in fileExtensions.video_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Videos'/item.name)
                vid_count += 1

            elif suffix_lower in fileExtensions.audio_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Audios'/item.name)
                aud_count += 1

            elif suffix_lower in fileExtensions.archive_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Archives'/item.name)
                arc_count += 1

            else:
                print(f"Organizing {item.name}")
                shutil.move(item, directory/'Others'/item.name)
                other_count += 1

        created_folders = {'Documents', 'Images', 'Videos', 'Audios', 'Archives', 'Others'}

        logging.debug('Removing empty non-category folders')
        for item in directory.iterdir():
            if item.is_dir() and item.name not in created_folders:
                try:
                    item.rmdir()
                except OSError as e:
                    logging.warning(f'Could not remove folder {item.name}: {e}')
                    pass

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        total_files = doc_count + img_count + vid_count + aud_count + arc_count + other_count
        logging.info(f'Organization complete. Organized {total_files} files in {elapsed_time:.1f} seconds')
        
        print('Created folders')
        print(f"\tDocuments ({doc_count}) files)")
        print(f"\tImages ({img_count}) files)")
        print(f"\tVideos ({vid_count}) files)")
        print(f"\tAudios ({aud_count}) files)")
        print(f"\tArchives ({arc_count}) files)")
        print(f"\tOthers ({other_count}) files)")
        print(f'Organized {total_files} files in {elapsed_time:.1f} seconds.')

    @staticmethod
    def manage_duplicates(args):
        logging.info(f'Starting manage_duplicates with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        min_size = args.min_size
        result = FileOrganizer._convert_to_bytes(min_size)

        if result is None:
            return

        min_size = result[0]

        logging.debug('Scanning directory for files to generate hashes')
        files = defaultdict(list)

        EXCLUDED_DIRS = {
            # Virtual environments
            '.venv', 'venv', 'env', 'virtualenv',
            # Package managers
            'node_modules', 'site-packages', 'dist-packages',
            # Caches
            '__pycache__', '.cache',
            # Version control
            '.git', '.svn', '.hg',
            # Build artifacts
            'dist', 'build', 'Debug', 'Release', 'obj', 'bin',
            # System directories
            'Library', 'AppData', 'ProgramData',
            # .NET
            '.dotnet', '.nuget',
        }

        for item in directory.rglob('*'):
            if not item.is_file():
                continue

            if any(part.startswith('.') for part in item.parts) or item.stat().st_size < min_size:
                continue

            # Check if any ancestor directory is in excluded list
            if not args.all:  # If --all is NOT specified, use exclusions
                if any(parent.name in EXCLUDED_DIRS for parent in item.parents):
                    continue

            file_hash = FileOrganizer._get_file_hash(item)
            files[file_hash].append(item)

        duplicates_found = any(len(duplicates) > 1 for duplicates in files.values())

        if not duplicates_found:
            logging.info('No duplicate files found')
            print('You have no duplicate files.')
            return

        logging.info('Duplicate files detected')
        total_space_wasted = 0

        for duplicates in files.values():
            if len(duplicates) > 1:
                wasted_space = sum(Path(file).stat().st_size for file in duplicates[:-1])
                total_space_wasted += wasted_space

        size, unit = FileOrganizer._find_unit(total_space_wasted)
        duplicate_count = sum(len(duplicates[:-1]) for duplicates in files.values() if len(duplicates) > 1)
        print(f'Found {duplicate_count} duplicate files, wasting {size} {unit}')

        duplicates_list = [duplicates for duplicates in files.values() if len(duplicates) > 1]

        for group_idx, duplicates in enumerate(duplicates_list, 1):
            print(f"\nDuplicate group {group_idx} ({len(duplicates)} files):")

            for i, file in enumerate(duplicates, 1):
                assert directory in file.parents
                relative = file.relative_to(directory)
                print(f"  {i}. {relative}")

        print("\n⚠️  WARNING")
        print("Deleted files will be permanently removed and cannot be recovered.\n")

        delete_options = input('Do you want to:\n'
                               '1. Delete all duplicates (keep newest)\n'
                               '2. Select files to delete\n'
                               '3. Continue without deleting\n'
                               '(1, 2 or 3) : ').strip()

        while delete_options not in ['1', '2', '3']:
            delete_options = input('Invalid choice, please select a valid option:\n'
                                   '1. Delete all duplicates (keep newest)\n'
                                   '2. Select files to delete\n'
                                   '3. Continue without deleting\n'
                                   '(1, 2 or 3) : ').strip()

        print('TO EXIT OPERATION, PRESS "Ctrl + C" AT ANY POINT')

        if delete_options == '1':

            confirm = input("All duplicates will be permanently deleted. Type DELETE to confirm, or anything else to cancel: ")
            if confirm != "DELETE":
                print("Operation cancelled. No files were deleted.")
                return

            for duplicates in duplicates_list:
                sorted_duplicated = sorted(duplicates, key=lambda f: f.stat().st_mtime, reverse=True)

                for f in sorted_duplicated[1:]:
                    try:
                        f.unlink()
                    except OSError as e:
                            logging.error(f'Failed to delete {f}: {e}')
                            print(f'{f} could not be deleted.')

            print(f'All duplicates deleted. Saved {size} {unit} of space.')

        elif delete_options == '2':

            freed_space = 0
            total_deleted = 0

            for duplicates in duplicates_list:
                print(f'{len(duplicates)} identical files in:')

                for i, file in enumerate(duplicates, 1):
                    assert directory in file.parents, "Invariant violated: file outside root directory"
                    relative = file.relative_to(directory)
                    print(f'\t{i}. {relative}')

                extra_size = sum(Path(file).stat().st_size for file in duplicates[:-1])
                size, unit = FileOrganizer._find_unit(extra_size)
                print(f'There are {size} {unit} of wasted space.')

                decision = input('Would you like to delete the duplicate files? [y/N]: ')
                if decision == 'y':
                    while True:
                        try:
                            choice = int(input(f'Enter number of file to keep (1 - {len(duplicates)}): '))
                            if 1 <= choice <= len(duplicates):
                                file_to_keep = duplicates[choice - 1]
                                break
                            else:
                                print(f"Please enter a number between 1 and {len(duplicates)}")
                        except ValueError:
                            print("Please enter a valid number.")

                    logging.info(f'User selected to keep file: {file_to_keep}')
                    for f in duplicates:
                        if f == file_to_keep:
                            continue

                        try:
                            freed_space += f.stat().st_size
                            f.unlink()
                            total_deleted += 1
                            print()

                        except OSError as e:
                            logging.error(f'Failed to delete {f}: {e}')
                            print(f'{f} could not be deleted.')
                            print()
                else:
                    print()
                    continue

            size, unit = FileOrganizer._find_unit(freed_space)
            logging.info(f'Deleted {total_deleted} duplicate files, freed {size} {unit}')
            print(f" You've deleted {total_deleted} files, and saved {size} {unit}")

        else:
            logging.info(f'User chose not to delete duplicates')
            print('Duplicates found but not deleted')

    @staticmethod
    def bulk_rename(args):
        logging.info(f'Starting bulk_rename with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        pattern = getattr(args, 'pattern', None)
        suffix = getattr(args, 'add_suffix', None)
        prefix = getattr(args, 'add_prefix', None)
        date = getattr(args, 'add_date', None)
        logging.debug(f'Rename options - Pattern: {pattern}, Suffix: {suffix}, Prefix: {prefix}, Date: {date}')

        if date:
            try:
                dt.strptime(date, '%Y-%m-%d')
                logging.debug(f'Date validation successful: {date}')
            except ValueError:
                logging.error(f'Invalid date format: {date}')
                print('Dates should be entered in the following format (YYYY-MM-DD)')
                return

        if pattern and any((suffix, prefix, date)):
            logging.error('Invalid options: pattern used with other attributes')
            print(
                "Invalid options: patterns must be used alone. "
                "Choose either a pattern, or one or more of the other attributes."
            )
            return

        valid_placeholders = {'{count}', '{name}', '{last_modified}', '{doc_type}'}

        all_files = [item for item in directory.iterdir() if item.is_file()]
        logging.debug(f'Found {len(all_files)} files to process')

        if pattern:
            logging.info(f'Processing files with pattern: {pattern}')
            found_placeholders = set(re.findall(r'(\{[^}]+\})', pattern))
            invalid_placeholders = found_placeholders - valid_placeholders

            if invalid_placeholders:
                logging.error(f'Invalid placeholders found: {invalid_placeholders}')
                print(f'Invalid placeholders: {invalid_placeholders}')
                print(f'Please select a valid placeholder in your pattern: {valid_placeholders}')
                return

            count = 0

            for file in all_files:
                ext = file.suffix
                new_name = pattern

                if '{name}' in found_placeholders:
                    new_name = new_name.replace('{name}', file.stem)

                if '{count}' in found_placeholders:
                    new_name = new_name.replace('{count}', str(count))

                if '{doc_type}' in found_placeholders:
                    suffix_lower = file.suffix.lower()
                    if suffix_lower in fileExtensions.document_extensions:
                        new_name = new_name.replace('{doc_type}', 'Document')
                    elif suffix_lower in fileExtensions.image_extensions:
                        new_name = new_name.replace('{doc_type}', 'Image')
                    elif suffix_lower in fileExtensions.video_extensions:
                        new_name = new_name.replace('{doc_type}', 'Video')
                    elif suffix_lower in fileExtensions.audio_extensions:
                        new_name = new_name.replace('{doc_type}', 'Audio')
                    elif suffix_lower in fileExtensions.archive_extensions:
                        new_name = new_name.replace('{doc_type}', 'Archive')
                    elif suffix_lower in fileExtensions.code_extensions:
                        new_name = new_name.replace('{doc_type}', 'Code')
                    elif suffix_lower in fileExtensions.web_extensions:
                        new_name = new_name.replace('{doc_type}', 'Web')
                    elif suffix_lower in fileExtensions.font_extensions:
                        new_name = new_name.replace('{doc_type}', 'Font')
                    elif suffix_lower in fileExtensions.executable_extensions:
                        new_name = new_name.replace('{doc_type}', 'Binary')
                    elif suffix_lower in fileExtensions.database_extensions:
                        new_name = new_name.replace('{doc_type}', 'Database')
                    else:
                        new_name = new_name.replace('{doc_type}', 'Other')

                if '{last_modified}' in found_placeholders:
                    last_modified = dt.fromtimestamp(file.stat().st_mtime)
                    readable_date = last_modified.strftime('%Y-%m-%d')
                    new_name = new_name.replace('{last_modified}', readable_date)

                if Path(new_name).suffix:
                    new_path = file.parent/f'{new_name}'
                else:
                    new_path = file.parent / f'{new_name}{ext}'

                if new_path.exists():
                    logging.warning(f'Cannot rename {file.stem}: target path already exists {new_path}')
                    print(f'{file.stem} cannot be renamed, {new_path}, because this file path already exists')
                    continue

                file.rename(new_path)
                count += 1

            logging.info(f'Pattern-based rename complete: renamed {count} files')

        if any((suffix, prefix, date)):
            logging.info(f'Processing files with prefix/suffix/date options')
            renamed_count = 0

            for file in all_files:
                ext = file.suffix
                new_name = file.stem

                if prefix:
                    new_name = f'{prefix}_{file.stem}'
                if date:
                    new_name = f'{new_name}_{date}'
                if suffix:
                    new_name = f'{new_name}_{suffix}'

                if Path(new_name).suffix:
                    new_path = file.parent/f'{new_name}'
                else:
                    new_path = file.parent / f'{new_name}{ext}'

                if new_path.exists():
                    logging.warning(f'Cannot rename {file.stem}: target path already exists {new_path}')
                    print(f'{file.stem} cannot be renamed, {new_path}, because this file path already exists')
                    continue

                file.rename(new_path)
                renamed_count += 1

            logging.info(f'Prefix/suffix/date rename complete: renamed {renamed_count} files')

    @staticmethod
    def find_large_files(args):
        logging.info(f'Starting find_large_files with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        # min_size comes as a string of size + unit (e.g. 100 MB), we have to convert it to bytes directly
        user_size = args.min_size.strip()
        logging.debug(f'User input size: {user_size}')

        result = FileOrganizer._convert_to_bytes(user_size)

        if result is None:
            return

        min_size, num_part, unit = result

        if args.recursive:
            logging.debug('Searching recursively through directory tree')
            large_files = [(item, item.stat().st_size) for item in directory.rglob('*') if item.is_file() and item.stat().st_size >= min_size]
        else:
            logging.debug('Searching only in top-level directory')
            large_files = [(item, item.stat().st_size) for item in directory.iterdir() if item.is_file() and item.stat().st_size >= min_size]

        sorted_files = sorted(large_files, key=lambda file : file[1])
        total_size = sum(file[1] for file in sorted_files)

        logging.info(f'Found {len(sorted_files)} files larger than {num_part} {unit}')
        print(f'Files above {num_part} {unit}')

        for file in sorted_files:
            f_size, f_unit = FileOrganizer._find_unit(file[1])
            print(f'{file[0]}: {f_size} {f_unit}')

        t_size, t_unit = FileOrganizer._find_unit(total_size)
        logging.info(f'Total size of large files: {t_size} {t_unit}')
        print(f'Total size: {t_size} {t_unit}.')

    @staticmethod
    def clean_up(args):
        logging.info(f'Starting clean_up with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        older_than = getattr(args, 'older_than', None)
        empty = getattr(args, 'empty_folder', None)
        logging.debug(f'Clean-up options - Older than: {older_than} days, Empty folders: {empty}')

        if not older_than and not empty:
            logging.error('No clean-up attribute specified')
            print('You must select an attribute; --older-than (number of days) or --empty-folder.')
            return

        if older_than and empty:
            logging.error('Multiple attributes specified (should be only one)')
            print('You can only select one attribute at a time.')
            return

        files_to_check = directory.rglob('*') if args.recursive else directory.iterdir()

        if older_than:
            logging.info(f'Searching for files older than {older_than} days')
            today = dt.today()
            cutoff = today - timedelta(days=older_than)
            old_files = []

            for item in files_to_check:
                if not item.is_file():
                    continue

                last_modified = dt.fromtimestamp(item.stat().st_mtime)

                if last_modified < cutoff:
                    old_files.append((item, item.stat().st_size))

            if not old_files:
                logging.info(f'No files older than {older_than} days found')
                print(f'There are no files older than {older_than} days.')
                return

            total_size = sum(file[1] for file in old_files)
            size, unit = FileOrganizer._find_unit(total_size)
            logging.warning(f'Found {len(old_files)} old files totaling {size} {unit}')

            print(f'You have {size} {unit} of old files.')
            old_paths = [p[0] for p in old_files]

            FileOrganizer._delete_path(old_paths, 'files')

        if empty:
            logging.info('Searching for empty folders')
            empty_folders = []

            for item in files_to_check:

                if not item.is_dir():
                    continue

                if not any(item.iterdir()):
                    empty_folders.append(item)

            if not empty_folders:
                logging.info('No empty folders found')
                print('No folders are empty in this directory')
                return

            logging.warning(f'Found {len(empty_folders)} empty folders')
            print(f'{len(empty_folders)} empty folders found')

            FileOrganizer._delete_path(empty_folders, 'folders')

    @staticmethod
    def walk_tree(args):
        logging.info(f'Starting walk_tree with directory: {args.directory}')
        directory = Path(args.directory).expanduser().resolve()
        logging.debug(f'Resolved directory path: {directory}')

        if not directory.exists():
            logging.error(f'Directory does not exist: {directory}')
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            logging.error(f'Path is not a directory: {directory}')
            print(f'{directory} is a file not a directory')
            return

        depth = getattr(args, 'depth', None)
        logging.debug(f'Tree depth limit: {depth}')

        FileOrganizer._tree(directory, depth)

    @staticmethod
    def _get_file_hash(filepath):
        try:
            hasher = hashlib.md5()

            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()
            return file_hash
        except OSError as e:
            logging.error(f'Error computing hash for {filepath}: {e}')
            raise

    @staticmethod
    def _find_unit(size:float) -> tuple[float, str]:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return round(size, 1), unit

            size /= 1024

        return round(size, 1), 'TB'

    @staticmethod
    def _convert_to_bytes(user_size):
        num_part = ''
        unit_part = ''

        for char in user_size:
            if char.isdigit() or char == '.':
                num_part += char
            else:
                unit_part = user_size[len(num_part):].strip()
                break

        if not num_part or not unit_part:
            logging.error(f'Invalid size format: {user_size}')
            print("Invalid format. Use format like: 100MB, 50 KB, 1.5GB")
            return

        try:
            min_size = float(num_part)
            logging.debug(f'Parsed size value: {min_size}')
        except ValueError:
            logging.error(f'Invalid number in size: {num_part}')
            print('Invalid number in size')
            return

        unit = unit_part.upper()

        conversion = {
            'B' : 1,
            'KB' : 1024,
            'MB' : 1024**2,
            'GB' : 1024**3,
            'TB' : 1024**4
        }

        if unit not in conversion:
            logging.error(f'Invalid unit: {unit}')
            print(f'{unit} is not a valid unit. Please select a valid unit: B, KB, MB, GB, & TB')
            return

        min_size = min_size * conversion[unit]
        logging.debug(f'Converted minimum size to bytes: {min_size}')

        return min_size, num_part, unit_part

    @staticmethod
    def _delete_path(paths:list, p_type:str):
        logging.info(f'Starting _delete_path for {len(paths)} {p_type}')

        delete_option = input("Would you like to:\n"
                           f"A. Delete all old {p_type}\n"
                           f"B. Delete selected {p_type} only\n"
                           "C. Continue without deleting\n"
                           "Select an option (A, B or C): ").upper()

        while delete_option not in ['A', 'B', 'C']:
            logging.warning(f'Invalid delete option selected: {delete_option}')
            delete_option =  input("Invalid choice. Please select a valid option (A, B, or C):\n"
                           f"A. Delete all old {p_type}\n"
                           f"B. Delete selected {p_type} only\n"
                           "C. Continue without deleting").upper()

        if delete_option == 'A':
            logging.info(f'User selected to delete all {len(paths)} {p_type}')
            for p in paths:
                if p.is_file():
                    try:
                        p.unlink()
                    except OSError as e:
                        logging.error(f'Failed to delete file {p}: {e}')
                        print(f'{p} could not be deleted.')

                elif p.is_dir():
                    try:
                        p.rmdir()
                    except OSError as e:
                        logging.error(f'Failed to delete directory {p}: {e}')
                        print(f'{p} could not be deleted.')

            logging.info(f'Deleted {len(paths)} {p_type}')
            print(f'{len(paths)} {p_type} deleted!')

        elif delete_option == 'B':
            logging.info(f'User selected to delete {p_type} selectively')
            paths_deleted = 0
            freed_space = 0

            for p in paths:
                delete_p = input(f'Would you like to delete {p}?[y/N]: ')

                if delete_p != 'y':
                    continue
                else:
                    if p.is_file():
                        try:
                            freed_space += p.stat().st_size
                            p.unlink()
                            paths_deleted += 1
                        except OSError as e:
                            logging.error(f'Failed to delete file {p}: {e}')
                            print(f'{p} could not be deleted.')

                    elif p.is_dir():
                        try:
                            p.rmdir()
                            paths_deleted += 1
                        except OSError as e:
                            logging.error(f'Failed to delete directory {p}: {e}')
                            print(f'{p} could not be deleted.')

            if p_type == 'files':
                size, unit = FileOrganizer._find_unit(freed_space)
                logging.info(f'Deleted {paths_deleted} files, freed {size} {unit}')
                print(f'{paths_deleted} files deleted ({size} {unit})')

            elif p_type == 'folders':
                logging.info(f'Deleted {paths_deleted} folders')
                print(f'{paths_deleted} folders deleted.')

        else:
            logging.info(f'User chose not to delete {p_type}')
            print(f'{p_type.capitalize()} found but not deleted:')
            for p in paths:
                print(p)

    # Implemented by AI, I was not familiar with the tree display algorithm
    @staticmethod
    def _tree(path: Path, depth, prefix=""):
        logging.debug(f'Traversing tree at {path} with depth {depth}')
        
        if depth is not None and depth < 0:
            logging.debug(f'Depth limit reached at {path}')
            return

        try:
            children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
            logging.debug(f'Found {len(children)} items in {path}')
        except PermissionError:
            logging.warning(f'Permission denied accessing {path}')
            print(prefix + "└── [permission denied]")
            return

        for index, item in enumerate(children):
            is_last = index == len(children) - 1
            connector = "└── " if is_last else "├── "

            print(prefix + connector + item.name)

            if item.is_dir() and not item.is_symlink():
                new_prefix = prefix + ("    " if is_last else "│   ")
                next_depth = None if depth is None else depth - 1
                FileOrganizer._tree(item, next_depth, new_prefix)

def main():
    logging.info('File Organizer application started2')

    organizer = FileOrganizer()

    parser = ArgumentParser(description='File Organizer and Duplicate Finder')
    subparsers = parser.add_subparsers(dest='commands', help='Available commands')

    # ==================== ORGANIZER ====================
    organize_subparser = subparsers.add_parser('organize', help='organize directory')
    organize_subparser.add_argument('directory', type=str, help='Directory name')
    organize_subparser.set_defaults(func=organizer.organize_dir)

    # ==================== DUPLICATES ====================
    duplicate_subparser = subparsers.add_parser('duplicate', help='organize directory')
    duplicate_subparser.add_argument('directory', type=str, help='Directory name')
    duplicate_subparser.add_argument('--min-size', default='1KB', help='Minimum file size to check (default: 1KB)')
    duplicate_subparser.add_argument('--all', action='store_true', help='Include system directories and virtual environments (not recommended)')
    duplicate_subparser.set_defaults(func=organizer.manage_duplicates)

    # ====================== RENAME ======================
    rename_subparser = subparsers.add_parser('rename', help='organize directory')
    rename_subparser.add_argument('directory', type=str, help='Directory name')
    rename_subparser.add_argument('--pattern', type=str, help='Pattern with placeholders: {name}, {count}, {doc_type}, {last_modified}')
    rename_subparser.add_argument('--add-prefix', type=str,  help='prefix to add to the file')
    rename_subparser.add_argument('--add-suffix', type=str,  help='suffix to add to the file')
    rename_subparser.add_argument('--add-date', type=str,  help='add a date (YYYY-MM-DD)')
    rename_subparser.set_defaults(func=organizer.bulk_rename)

   # ==================== FIND LARGE ====================
    find_large_subparser = subparsers.add_parser('find-large', help='organize directory name')
    find_large_subparser.add_argument('directory', type=str, help='Directory')
    find_large_subparser.add_argument('--min-size', type=str, required=True, help='minimum size of files to find (e.g. 100 MB)')
    find_large_subparser.add_argument('--recursive', action='store_true', help='look through the entire directory tree')
    find_large_subparser.set_defaults(func=organizer.find_large_files)

   # ===================== CLEANUP ======================
    cleanup_subparser = subparsers.add_parser('clean-up', help='organize directory')
    cleanup_subparser.add_argument('directory', type=str, help='Directory name')
    cleanup_subparser.add_argument('--older-than', type=int, help='Files older the x days')
    cleanup_subparser.add_argument('--empty-folder', action='store_true',  help='Finds all empty folders')
    cleanup_subparser.add_argument('--recursive', action='store_true',  help='Finds all empty folders')
    cleanup_subparser.set_defaults(func=organizer.clean_up)

    # ====================== TREE =======================
    rename_subparser = subparsers.add_parser('tree', help='organize directory')
    rename_subparser.add_argument('directory', type=str, help='Directory name')
    rename_subparser.add_argument('--depth', required=True, type=int, help='Depth of the directory tree')
    rename_subparser.set_defaults(func=organizer.walk_tree)

    args = parser.parse_args()
    logging.debug(f'Parsed arguments: {args}')

    if hasattr(args, 'func'):
        logging.info(f'Executing command: {args.commands}')
        args.func(args)
    else:
        logging.info('No command specified, printing help')
        parser.print_help()

if __name__ == '__main__':
    main()