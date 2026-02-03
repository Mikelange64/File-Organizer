from argparse import ArgumentParser
from pathlib import Path
import shutil
import os
import hashlib
import json
import datetime
import time
import logging
from collections import defaultdict
from time import sleep

from fileExtensions import image_extensions, video_extensions, document_extensions, audio_extensions, archive_extensions


class FileOrganizer:

    @staticmethod
    def organize_dir(args):
        directory = Path(args.directory)

        if not directory.exists():
            print('This directory does not exist')
            return

        (directory/'Documents').mkdir(exist_ok=True, parents=True)
        (directory/'Images').mkdir(exist_ok=True, parents=True)
        (directory/'Videos').mkdir(exist_ok=True, parents=True)
        (directory/'Audios').mkdir(exist_ok=True, parents=True)
        (directory/'Archives').mkdir(exist_ok=True, parents=True)
        (directory/'Others').mkdir(exist_ok=True, parents=True)

        documents = document_extensions
        images = image_extensions
        videos = video_extensions
        audio = audio_extensions
        archives = archive_extensions

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

            if suffix_lower in documents:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Documents'/item))
                doc_count += 1

            elif suffix_lower in images:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Images'/item))
                img_count += 1

            elif suffix_lower() in videos:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory / 'Videos'/item))
                vid_count += 1

            elif suffix_lower() in audio:
                print(f"Organizing {item.name}")
                shutil.move(item, Path(directory/'Audios'/item))
                aud_count += 1

            elif suffix_lower() in archives:
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
                        freed_space += Path(f).stat().st_size
                        total_deleted += 1

                        try:
                            Path(f).unlink()
                        except OSError as e:
                            print(e)
                            print(f'{f} could not be deleted.')

        size, unit = FileOrganizer._find_unit(freed_space)
        print(f" You've deleted {total_deleted} files, and saved {size} {unit}")

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
    def _find_unit(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return round(size, 1), unit

            size /= 1024

def main():

    organizer = FileOrganizer()

    parser = ArgumentParser(description='File Organizer and Duplicate Finder')
    subparsers = parser.add_subparsers(dest='commands', help='Available commands')

    # ==================== ORGANIZER ====================
    organize_subparser = subparsers.add_parser('organize', help='organize directory')
    organize_subparser.add_argument('directory', type=str, required=True, help='The directory to organize')
    organize_subparser.set_defaults(func=organizer.organize_dir)

    # ==================== DUPLICATES ====================
    duplicate_subparser = subparsers.add_parser('duplicate', help='organize directory')
    duplicate_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    duplicate_subparser.add_argument('--scan', action='store_true', help='scan directory for duplicates')
    duplicate_subparser.add_argument('--remove', action='store_true',  help='remove duplicates from directory')
    duplicate_subparser.set_defaults(func=organizer.manage_duplicates)

    # ====================== RENAME ======================
    rename_subparser = subparsers.add_parser('rename', help='organize directory')
    rename_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    rename_subparser.add_argument('--pattern', action='store_true', help='scan directory for duplicates')
    rename_subparser.add_argument('--add-prefix', action='store_true',  help='remove duplicates from directory')
    rename_subparser.add_argument('--add-date', action='store_true',  help='remove duplicates from directory')
    rename_subparser.set_defaults(func='')

   # ==================== DUPLICATES ====================
    duplicate_subparser = subparsers.add_parser('rename', help='organize directory')
    duplicate_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    duplicate_subparser.add_argument('--pattern', action='store_true', help='scan directory')
    duplicate_subparser.add_argument('--add-prefix', action='store_true',  help='remove duplicates from directory')
    duplicate_subparser.add_argument('--add-date', action='store_true',  help='remove duplicates from directory')
    duplicate_subparser.set_defaults(func='')

   # ==================== FIND LARGE ====================
    find_large_subparser = subparsers.add_parser('find-large', help='organize directory')
    find_large_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    find_large_subparser.add_argument('--min-size', type=str, help='minimum size of files to find')
    find_large_subparser.set_defaults(func='')

   # ===================== CLEANUP ======================
    cleanup_subparser = subparsers.add_parser('clean-up', help='organize directory')
    cleanup_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    cleanup_subparser.add_argument('--older-than', type=int, help='Age of files to find')
    cleanup_subparser.add_argument('--empty-folder', type=str,  help='Finds all empty folders')
    cleanup_subparser.set_defaults(func='')

    # ===================== CLEANUP ======================
    rename_subparser = subparsers.add_parser('clean-up', help='organize directory')
    rename_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    rename_subparser.add_argument('--older-than', type=int, help='Age of files to find')

    # ====================== TREE =======================
    rename_subparser = subparsers.add_parser('tree', help='organize directory')
    rename_subparser.add_argument('directory', type=str, required=True, help='Directory to inspect')
    rename_subparser.add_argument('--depth', type=int, help='Depth of the directory tree')

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()