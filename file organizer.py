from argparse import ArgumentParser
from pathlib import Path
import shutil
import re
import hashlib
from datetime import datetime as dt, timedelta
import time
from collections import defaultdict
import fileExtensions


class FileOrganizer:

    @staticmethod
    def organize_dir(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        (directory/'Documents').mkdir(exist_ok=True, parents=True)
        (directory/'Images').mkdir(exist_ok=True, parents=True)
        (directory/'Videos').mkdir(exist_ok=True, parents=True)
        (directory/'Audios').mkdir(exist_ok=True, parents=True)
        (directory/'Archives').mkdir(exist_ok=True, parents=True)
        (directory/'Others').mkdir(exist_ok=True, parents=True)

        doc_count = 0
        img_count = 0
        vid_count = 0
        aud_count = 0
        arc_count = 0
        other_count = 0

        start_time = time.perf_counter()

        for item in list(directory.iterdir()):

            if not item.is_file():
                continue

            suffix_lower = item.suffix.lower()


            if suffix_lower in fileExtensions.document_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Documents'/item))
                doc_count += 1

            elif suffix_lower in fileExtensions.image_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Images'/item))
                img_count += 1

            elif suffix_lower() in fileExtensions.video_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory / 'Videos'/item))
                vid_count += 1

            elif suffix_lower() in fileExtensions.audio_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Audios'/item))
                aud_count += 1

            elif suffix_lower() in fileExtensions.archive_extensions:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Archives'/item))
                arc_count += 1

            else:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Others'/item))
                other_count += 1

        created_folders = {'Documents', 'Images', 'Videos', 'Audios', 'Archives', 'Others'}

        for item in directory.iterdir():
            if item.is_dir() and item.name not in created_folders:
                try:
                    item.rmdir()
                except OSError:
                    pass

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        print('Create folders')
        print(f"\tDocuments ({doc_count}) files)")
        print(f"\tImages ({img_count}) files)")
        print(f"\tVideos ({vid_count}) files)")
        print(f"\tAudios ({aud_count}) files)")
        print(f"\tArchives ({arc_count}) files)")
        print(f"\tOthers ({other_count}) files)")
        print(f'Organized {doc_count + img_count + vid_count + aud_count + arc_count + other_count} files in {elapsed_time:.1f} seconds.')

    @staticmethod
    def manage_duplicates(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        files = defaultdict(list)

        for item in directory.rglob('*'):
            if item.is_file():
                file_hash = FileOrganizer._get_file_hash(item)
                files[file_hash].append(item)

        if not any(len(duplicates) > 1 for duplicates in files.values()):
            print('You have no duplicate files.')
            return

        total_space_wasted = 0
        for duplicates in files.values():
            if len(duplicates) > 1:
                wasted_space = sum(Path(file).stat().st_size for file in duplicates[:-1])
                total_space_wasted += wasted_space

        size, unit = FileOrganizer._find_unit(total_space_wasted)
        print(f"You have {sum(len(duplicates[:-1]) for duplicates in files.values() if len(duplicates) > 1)} duplicate files, {size} {unit} of wasted space.")

        freed_space = 0
        total_deleted = 0

        for duplicates in files.values():
            if len(duplicates) > 1:
                print(f'{len(duplicates)} identical files:')

                for file in duplicates:
                    print(f'\t- {Path(file).name}')

                extra_size = sum(Path(file).stat().st_size for file in duplicates[:-1])
                size, unit = FileOrganizer._find_unit(extra_size)

                print(f'There are {size} {unit} of wasted space.')

                decision = input('Would you like to delete the duplicate files? [y/N]: ')
                if decision == 'y':
                    file_to_keep = input('Which file would you like to keep?: ')
                    f_names_with_ext = [Path(f).name for f in duplicates]
                    f_names = [Path(f).stem for f in duplicates]

                    while file_to_keep not in f_names_with_ext and file_to_keep not in f_names:
                        file_to_keep = input('This is not a valid file, which file would you like to keep: ')

                    for f in duplicates:
                        if Path(f).name == file_to_keep or Path(f).stem == file_to_keep:
                            continue

                        try:
                            Path(f).unlink()
                            freed_space += Path(f).stat().st_size
                            total_deleted += 1
                        except OSError as e:
                            print(e)
                            print(f'{f} could not be deleted.')

        size, unit = FileOrganizer._find_unit(freed_space)
        print(f" You've deleted {total_deleted} files, and saved {size} {unit}")

    @staticmethod
    def bulk_rename(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        pattern = getattr(args, 'pattern', None)
        suffix = getattr(args, 'add_suffix', None)
        prefix = getattr(args, 'add_prefix', None)
        date = getattr(args, 'add_date', None)

        if date:
            try:
                dt.strptime(date, '%Y-%m-%d')
            except ValueError:
                print('Dates should be entered in the following format (YYYY-MM-DD)')
                return

        if pattern and any((suffix, prefix, date)):
            print(
                "Invalid options: patterns must be used alone. "
                "Choose either a pattern, or one or more of the other attributes."
            )
            return

        valid_placeholders = {'{count}', '{name}', '{last_modified}', '{doc_type}'}

        all_files = [item for item in directory.iterdir() if item.is_file()]

        if pattern:
            found_placeholders = set(re.findall(r'(\{[^}]+\})', pattern))
            invalid_placeholders = found_placeholders - valid_placeholders

            if invalid_placeholders:
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
                    print(f'{file.stem} cannot be renamed, {new_path}, because this file path already exists')
                    continue

                file.rename(new_path)
                count += 1

        if any((suffix, prefix, date)):

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
                    print(f'{file.stem} cannot be renamed, {new_path}, because this file path already exists')
                    continue

                file.rename(new_path)

    @staticmethod
    def find_large_files(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        # min_size comes as a string of size + unit (e.g. 100 MB), we have to convert it to bytes directly
        user_size = args.min_size.strip()
        num_part = ''
        unit_part = ''

        for char in user_size:
            if char.isdigit() or char == '.':
                num_part += char
            else:
                unit_part = user_size[len(num_part):].strip()
                break

        if not num_part or not unit_part:
            print("Invalid format. Use format like: 100MB, 50 KB, 1.5GB")
            return

        try:
            min_size = float(num_part)
        except ValueError:
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
            print(f'{unit} is not a valid unit. Please select a valid unit: B, KB, MB, GB, & TB')
            return

        min_size = min_size * conversion[unit]

        if args.recursive:
            large_files = [(item, item.stat().st_size) for item in directory.rglob('*') if item.is_file() and item.stat().st_size >= min_size]
        else:
            large_files = [(item, item.stat().st_size) for item in directory.iterdir() if item.is_file() and item.stat().st_size >= min_size]

        sorted_files = sorted(large_files, key=lambda file : file[1])
        total_size = sum(file[1] for file in sorted_files)

        print(f'Files above {num_part} {unit}')

        for file in sorted_files:
            f_size, f_unit = FileOrganizer._find_unit(file[1])
            print(f'{file[0]}: {f_size} {f_unit}')

        t_size, t_unit = FileOrganizer._find_unit(total_size)
        print(f'Total size: {t_size} {t_unit}.')

    @staticmethod
    def clean_up(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        older_than = getattr(args, 'older_than', None)
        empty = getattr(args, 'empty_folder', None)

        if not older_than and not empty:
            print('You must select an attribute; --older-than (number of days) or --empty-folder.')
            return

        if older_than and empty:
            print('You can only select one attribute at a time.')
            return

        files_to_check = directory.rglob('*') if args.recursive else directory.iterdir()

        if older_than:
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
                print(f'There are no files older than {older_than} days.')
                return

            total_size = sum(file[1] for file in old_files)
            size, unit = FileOrganizer._find_unit(total_size)

            print(f'You have {size} {unit} of old files.')
            old_paths = [p[0] for p in old_files]

            FileOrganizer._delete_path(old_paths, 'files')

        if empty:
            empty_folders = []

            for item in files_to_check:

                if not item.is_dir():
                    continue

                if not any(item.iterdir()):
                    empty_folders.append(item)

            if not empty_folders:
                print('No folders are empty in this directory')
                return

            print(f'{len(empty_folders)} empty folders found')

            FileOrganizer._delete_path(empty_folders, 'folders')

    @staticmethod
    def walk_tree(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist.')
            return

        if not directory.is_dir():
            print(f'{directory} is a file not a directory')
            return

        depth = getattr(args, 'depth', None)

        FileOrganizer._tree(directory, depth)

    @staticmethod
    def _get_file_hash(filepath):
        hasher = hashlib.md5()

        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def _find_unit(size:float) -> tuple[float, str]:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return round(size, 1), unit

            size /= 1024

        return round(size, 1), 'TB'

    @staticmethod
    def _delete_path(paths:list, p_type:str):

        delete_option = input("Would you like to:\n"
                           f"A. Delete all old {p_type}\n"
                           f"B. Delete selected {p_type} only\n"
                           "C. Continue without deleting\n"
                           "Select an option (A, B or C): ").upper()

        while delete_option not in ['A', 'B', 'C']:
            delete_option =  input("Invalid choice. Please select a valid option (A, B, or C):\n"
                           f"A. Delete all old {p_type}\n"
                           f"B. Delete selected {p_type} only\n"
                           "C. Continue without deleting").upper()

        if delete_option == 'A':
            for p in paths:
                if p.is_file():
                    try:
                        p.unlink()
                    except OSError:
                        print(f'{p} could not be deleted.')

                elif p.is_dir():
                    try:
                        p.rmdir()
                    except OSError:
                        print(f'{p} could not be deleted.')

            print(f'{len(paths)} {p_type} deleted!')

        elif delete_option == 'B':
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
                        except OSError:
                            print(f'{p} could not be deleted.')

                    elif p.is_dir():
                        try:
                            p.rmdir()
                            paths_deleted += 1
                        except OSError:
                            print(f'{p} could not be deleted.')

            if p_type == 'files':
                size, unit = FileOrganizer._find_unit(freed_space)
                print(f'{paths_deleted} files deleted ({size} {unit})')

            elif p_type == 'folders':
                print(f'{paths_deleted} folders deleted.')

        else:
            print(f'{p_type.capitalize()} found but not deleted:')
            for p in paths:
                print(p)

    # Implemented by AI, I was not familiar with the tree display algorithm
    @staticmethod
    def _tree(path: Path, depth, prefix=""):
        if depth is not None and depth < 0:
            return

        try:
            children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
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

    organizer = FileOrganizer()

    parser = ArgumentParser(description='File Organizer and Duplicate Finder')
    subparsers = parser.add_subparsers(dest='commands', help='Available commands')

    # ==================== ORGANIZER ====================
    organize_subparser = subparsers.add_parser('organize', help='organize directory')
    organize_subparser.add_argument('directory', type=str, required=True, help='Directory name')
    organize_subparser.set_defaults(func=organizer.organize_dir)

    # ==================== DUPLICATES ====================
    duplicate_subparser = subparsers.add_parser('duplicate', help='organize directory')
    duplicate_subparser.add_argument('directory', type=str, required=True, help='Directory name')
    duplicate_subparser.add_argument('--scan', action='store_true', help='scan directory for duplicates')
    duplicate_subparser.set_defaults(func=organizer.manage_duplicates)

    # ====================== RENAME ======================
    rename_subparser = subparsers.add_parser('rename', help='organize directory')
    rename_subparser.add_argument('directory', type=str, required=True, help='Directory name')
    rename_subparser.add_argument('--pattern', type=str, help='Pattern with placeholders: {name}, {count}, {doc_type}, {last_modified}')
    rename_subparser.add_argument('--add-prefix', type=str,  help='prefix to add to the file')
    rename_subparser.add_argument('--add-suffix', type=str,  help='suffix to add to the file')
    rename_subparser.add_argument('--add-date', type=str,  help='add a date (YYYY-MM-DD)')
    rename_subparser.set_defaults(func=organizer.bulk_rename)

   # ==================== FIND LARGE ====================
    find_large_subparser = subparsers.add_parser('find-large', help='organize directory name')
    find_large_subparser.add_argument('directory', type=str, required=True, help='Directory')
    find_large_subparser.add_argument('--min-size', type=str, required=True, help='minimum size of files to find (e.g. 100 MB)')
    find_large_subparser.add_argument('--recursive', action='store_true', help='look through the entire directory tree')
    find_large_subparser.set_defaults(func=organizer.find_large_files)

   # ===================== CLEANUP ======================
    cleanup_subparser = subparsers.add_parser('clean-up', help='organize directory')
    cleanup_subparser.add_argument('directory', type=str, required=True, help='Directory name')
    cleanup_subparser.add_argument('--older-than', type=int, help='Files older the x days')
    cleanup_subparser.add_argument('--empty-folder', action='store_true',  help='Finds all empty folders')
    cleanup_subparser.add_argument('--recursive', action='store_true',  help='Finds all empty folders')
    cleanup_subparser.set_defaults(func=organizer.clean_up)

    # ====================== TREE =======================
    rename_subparser = subparsers.add_parser('tree', help='organize directory')
    rename_subparser.add_argument('directory', type=str, required=True, help='Directory name')
    rename_subparser.add_argument('--depth', required=True, type=int, help='Depth of the directory tree')
    rename_subparser.set_defaults(func=organizer.walk_tree)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()