from argparse import ArgumentParser
import json
import os
import datetime
import logging
import time
from pathlib import Path
import shutil
from fileExtensions import image_extensions, video_extensions, document_extensions, audio_extensions, archive_extensions


class FileOrganizer:

    def __init__(self):
        pass

    def organize_dir(self, args):
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
    duplicate_subparser.set_defaults(func='')

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