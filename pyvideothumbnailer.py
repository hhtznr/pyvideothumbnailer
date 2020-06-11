#!/usr/bin/python3

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from argparse import Namespace

import os

VIDEO_EXTENSIONS = ('.avi',
                    '.divx',
                    '.flv',
                    '.m4v',
                    '.mkv',
                    '.mov',
                    '.mp4',
                    '.mpg',
                    '.wmv')

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

def parse_args() -> Namespace:
    parser = ArgumentParser(description='Pyhton Video Thumbnailer. Command line tool for creating video preview thumbnails.',
                            formatter_class=ArgumentDefaultsHelpFormatter)
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
