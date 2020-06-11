#!/usr/bin/python3

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from argparse import Namespace

import os
import sys

VIDEO_EXTENSIONS = ('.avi',
                    '.divx',
                    '.flv',
                    '.m4v',
                    '.mkv',
                    '.mov',
                    '.mp4',
                    '.mpg',
                    '.wmv')

def create_preview_thumbnails(file_path: str) -> None:
    """
    Create preview thumbnails of a video file.

    Parameters:
    file_path (str): The path of the video file of which to create thumbnails.
    """
    print('Creating preview thumbnails for \'{}\' ...'.format(os.path.abspath(file_path)))

def has_video_extension(file_name: str) -> bool:
    """
    Checks if a file name ends with a video extension.

    Checks if the provided file name ends with an extension that is common
    for video files. The check is case-insensitive.

    Parameters:
    file_name (str): The file name to check.

    Returns:
    bool: True if the file name ends with a common video extension, False otherwise.
    """
    return file_name.lower().endswith(VIDEO_EXTENSIONS)

def process_file_or_directory(path: str, recursive: bool) -> None:
    """
    Process a file or directory and create preview thumbnails of identified video files.

    If called on a file, preview thumbnails are created if the file is a video.
    If called on a directory, preview thumbnails are created of video files found in the directory.

    Parameters:
    path (str): The absolute or relative path of the file or directory.
    recursive (bool): If path is a directory and True, process any subdirectories as well.
    """
    # List of files and directories to process
    file_names = None
    # If the path is a directory, list its contents
    if os.path.isdir(path):
        file_names = sorted(os.listdir(path))
    # If the path is a file, get its dirname and basename
    elif os.path.isfile(path):
        path_elements = os.path.split(path)
        # dirname
        path = path_elements[0]
        # basename (as sole element in a list to be compatible with iteration below)
        file_names = [path_elements[1]]
    else:
        print('Path \'{}\' is neither a file nor a directory.'.format(os.path.abspath(path)))
        return

    # If path is a directory, iterate over the contained files and directories.
    # If path is a file, just 'iterate' over this single file.
    for file_name in file_names:
        file_path = os.path.join(path, file_name)
        # If recursive, call the process method on any subdirectories
        if recursive and os.path.isdir(file_path):
            process_file_or_directory(file_path, True)
        # Create preview thumbnails of (potential) video files
        elif os.path.isfile(file_path) and has_video_extension(file_name):
            try:
                create_preview_thumbnails(file_path)
            except Exception as e:
                print('An exception occurred: {}.\nSkipping file \'{}\'.'.format(e, os.path.abspath(file_path)), file=sys.stderr)

def parse_args() -> Namespace:
    parser = ArgumentParser(description='Pyhton Video Thumbnailer. Command line tool for creating video preview thumbnails.',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--recursive',
                         action='store_true',
                         help='If creating preview thumbnails of video files in a directory, process subdirectories recursively.')
    parser.add_argument('filename',
                         nargs='?',
                         type=str,
                         default=os.getcwd(),
                         help="""Video file of which to create preview thumbnails or directory, where multiple video files are located.
                         File name in the current working directory or path. If the argument is omitted, preview thumbnails are
                         generated for video files in the current working directory.""")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    process_file_or_directory(args.filename, args.recursive)
