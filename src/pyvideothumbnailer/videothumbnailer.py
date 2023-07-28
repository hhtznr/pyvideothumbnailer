#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python Video Thumbnailer

Pyhton Video Thumbnailer is a command line tool for creating video preview thumbnails.
It can be used to create preview images of individual video files, videos located in
a directory and optionally its subdirectories.

It is based on PyAV, MediaInfo and PIL/Pillow.

For usage and available options, run with the option ```--help```.

For further reference: https://github.com/hhtznr/pyvideothumbnailer/wiki
"""

from __future__ import annotations

from pathlib import Path
import os
import sys

from argparse import ArgumentParser
from argparse import Namespace

from configparser import ConfigParser

# Library for accessing metadata and other media information (https://github.com/sbraz/pymediainfo)
from pymediainfo import MediaInfo

# Library for video editing (https://github.com/PyAV-Org/PyAV)
import av

# Python imaging library (https://python-pillow.org/)
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

__author__ = 'Harald Hetzner'
__license__ = 'BSD 3-Clause License'
__version__ = '2.0.3'

class Parameters:
    """
    Parameters of Python Video Thumbnailer.
    """

    DEFAULT_PATH = Path.cwd()
    DEFAULT_RECURSIVE = False
    DEFAULT_WIDTH = 800
    DEFAULT_COLUMNS = 4
    DEFAULT_ROWS = 3
    DEFAULT_VERTICAL_VIDEO_COLUMNS = None
    DEFAULT_VERTICAL_VIDEO_ROWS = None
    DEFAULT_SPACING = 2
    DEFAULT_BACKGROUND_COLOR = 'white'
    DEFAULT_NO_HEADER = False
    DEFAULT_HEADER_FONT_NAME = None
    DEFAULT_HEADER_FONT_SIZE = 14
    DEFAULT_HEADER_FONT_COLOR = 'black'
    DEFAULT_TIMESTAMP_FONT_NAME = None
    DEFAULT_TIMESTAMP_FONT_SIZE = 12
    DEFAULT_TIMESTAMP_FONT_COLOR = 'white'
    DEFAULT_TIMESTAMP_SHADOW_COLOR = 'black'
    DEFAULT_COMMENT_LABEL = 'Comment:'
    DEFAULT_COMMENT_TEXT = None
    DEFAULT_SKIP_SECONDS = 10.0
    DEFAULT_SUFFIX = None
    DEFAULT_JPEG_QUALITY = 95
    DEFAULT_OVERRIDE_EXISTING = False
    DEFAULT_OUTPUT_DIRECTORY = None
    DEFAULT_RAISE_ERRORS = False
    DEFAULT_VERBOSE = False

    def __init__(self, path: Path, recursive: bool, width: int, columns: int, rows: int,
                 vertical_video_columns: int, vertical_video_rows: int, spacing: int,
                 background_color: str, no_header: bool, header_font_name: str, header_font_size: int, header_font_color: str,
                 timestamp_font_name: str, timestamp_font_size: int, timestamp_font_color: str, timestamp_shadow_color: str,
                 comment_label: str, comment_text: str,
                 skip_seconds: float, suffix: str, jpeg_quality: int, override_existing: bool, output_directory: Path,
                 raise_errors: bool, verbose: bool):
        """
        Constructor for an instance of the object holding all of the parameters of Python Video Thumbnailer.

        Parameters:
        path (Path): The path of the video file of which to create a preview thumbnails image
                     or the path of the directory, where video files are located of which to create preview images.
        recursive (bool): If path is a directory and True, process any subdirectories as well.
        width (int): The width in pixels of the created preview thumbnails image.
        columns (int): The number of thumbnail columns.
        rows (int): The number of thumbnail rows.
        vertical_video_columns (int): The number of preview thumbnail columns in place of argument \'columns\' in case of vertical videos.
                                      May be set to None in order to use the same number of columns for vertical and horizontal videos.
        vertical_video_rows (int): The number of preview thumbnail rows in place of argument \'rows\' in case of vertical videos.
                                   May be set to None in order to use the same number of rows for vertical and horizontal videos.
        spacing (int): The spacing in pixels between and around the preview thumbnails.
        background_color (str): Name or other definition of the PIL color to use for the image background,
                                for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
        no_header (bool): Do not include a header with metadata and optional comment. Enabling this option will make all header settings irrelevant.
        header_font_name (str): The name of a true type font to use for the header text providing information on the video file and its metadata.
                                If omitted, a built-in default font is used.
        header_font_size (int): The font size of the header font, if a true type font is specified. With the built-in font, this value is ignored.
        header_font_color (str): Name or other definition of the PIL color to use for the header font,
                                 for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
        timestamp_font_name (str): The name of a true type font to use for the preview thumbnail timestamps.
                                   If omitted, a built-in default font is used.
        timestamp_font_size (str): The font size of the timestamp font, if a true type font is specified. With the built-in font, this value is ignored.
        timestamp_font_color (str): Name or other definition of the PIL color to use for the timestamp font,
                                    for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
        timestamp_shadow_color (str): Name or other definition of the PIL color to use for the shadow of the timestamps,
                                      for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
                                      May be None to suppress drawing of a text shadow.
        comment_label (str): The label string of an optional user-defined comment added at the bottom of the video metadata information.
                             If not defined, the default label 'Comment:' is used.
        comment_text (str): An optional user-defined comment added added at the bottom of the video metadata information.
                            If not defined, no comment is added and the respective text line is omitted in the header.
        skip_seconds (float): The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail.
        suffix (str): An optional suffix to append to the file name of the generated preview thumbnails images.
        jpeg_quality (int): The quality of the JPEG image file that is created.
        override_existing (bool): If True, override image files that exist by the same name as the created image files.
        output_directory (Path): A directory, where all created preview thumbnails images should be saved.
                                 If omitted, preview thumbnails images are saved in the same directory, where the respective video file is located.
        raise_errors (bool): If True, raise an error, if it occurs during processing. If False, just print the error and proceed.
        verbose (bool): Print verbose information and messages.
        """
        self.path = path
        self.recursive = recursive
        self.width = width
        self.columns = columns
        self.rows = rows
        self.vertical_video_columns = vertical_video_columns
        self.vertical_video_rows = vertical_video_rows
        self.spacing = spacing
        self.background_color = ImageColor.getrgb(background_color)
        self.no_header = no_header
        self.header_font_name = header_font_name
        self.header_font_size = header_font_size
        self.header_font_color = ImageColor.getrgb(header_font_color)
        self.timestamp_font_name = timestamp_font_name
        self.timestamp_font_size = timestamp_font_size
        self.timestamp_font_color = ImageColor.getrgb(timestamp_font_color)
        self.timestamp_shadow_color = None
        if timestamp_shadow_color is not None:
            self.timestamp_shadow_color = ImageColor.getrgb(timestamp_shadow_color)
        self.comment_label = comment_label
        self.comment_text = comment_text
        self.skip_seconds = skip_seconds
        self.suffix = suffix
        self.jpeg_quality = jpeg_quality
        self.override_existing = override_existing
        self.output_directory = output_directory
        self.raise_errors = raise_errors
        self.verbose = verbose

    @staticmethod
    def from_defaults() -> Parameters.Parameters:
        """
        Returns the default parameters for Python Video Thumbnailer.

        Returns:
        Parameters: The Pyhton Video Thumbnailer parameters, initialized with the default values.
        """
        return Parameters(Parameters.DEFAULT_PATH,
                          Parameters.DEFAULT_RECURSIVE,
                          Parameters.DEFAULT_WIDTH,
                                          Parameters.DEFAULT_COLUMNS,
                                          Parameters.DEFAULT_ROWS,
                                          Parameters.DEFAULT_VERTICAL_VIDEO_COLUMNS,
                                          Parameters.DEFAULT_VERTICAL_VIDEO_ROWS,
                                          Parameters.DEFAULT_SPACING,
                                          Parameters.DEFAULT_BACKGROUND_COLOR,
                                          Parameters.DEFAULT_NO_HEADER,
                                          Parameters.DEFAULT_HEADER_FONT_NAME,
                                          Parameters.DEFAULT_HEADER_FONT_SIZE,
                                          Parameters.DEFAULT_HEADER_FONT_COLOR,
                                          Parameters.DEFAULT_TIMESTAMP_FONT_NAME,
                                          Parameters.DEFAULT_TIMESTAMP_FONT_SIZE,
                                          Parameters.DEFAULT_TIMESTAMP_FONT_COLOR,
                                          Parameters.DEFAULT_TIMESTAMP_SHADOW_COLOR,
                                          Parameters.DEFAULT_COMMENT_LABEL,
                                          Parameters.DEFAULT_COMMENT_TEXT,
                                          Parameters.DEFAULT_SKIP_SECONDS,
                                          Parameters.DEFAULT_SUFFIX,
                                          Parameters.DEFAULT_JPEG_QUALITY,
                                          Parameters.DEFAULT_OVERRIDE_EXISTING,
                                          Parameters.DEFAULT_OUTPUT_DIRECTORY,
                                          Parameters.DEFAULT_RAISE_ERRORS,
                                          Parameters.DEFAULT_VERBOSE)

class ConfigFile:
    """
    Configuration file of Pyhton Video Thumbnailer.
    """

    CONFIG_FILE_NAME = '.pyvideothumbnailer.conf'

    CONFIG_SECTION_LAYOUT = 'Layout'
    CONFIG_SECTION_HEADER = 'Header'
    CONFIG_SECTION_VIDEO = 'Video'
    CONFIG_SECTION_FILE = 'File'
    CONFIG_SECTION_PROGRAM = 'Program'

    @staticmethod
    def get_config_file_path() -> Path:
        """
        Returns the path, where the user configuration file of Python Video Thumbnailer is expected.

        Returns:
        Path: The absolute path of the user configuration file of Python Video Thumbnailer.
        """
        return Path.home() / ConfigFile.CONFIG_FILE_NAME

class Helper:
    """
    Class with static helper methods for Python Video Thumbnailer.
    """

    @staticmethod
    def format_size(size: int, suffix: str = 'B') -> str:
        """
        Formats an integer size value to make it human-readable.

        Parameters:
        size (int): The size value to format.
        suffix (str): The suffix denoting the base unit, default: 'B' for byte

        Returns:
        str: A human-readable representation of the size value.
        """
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(size) < 1024.0:
                return '{:.2f} {}{}'.format(size, unit, suffix)
            size /= 1024.0
        return '{:.2f} {}{}'.format(size, 'Yi', suffix)

    @staticmethod
    def format_time(duration_in_seconds: float) -> str:
        """
        Formats a duration in seconds to make it human-readable.

        Parameters:
        duration_in_seconds (float): The duration in seconds.

        Returns:
        str: A human-readable representation of the duration.
        """
        # Parse duration and cast to full seconds
        duration = int(float(duration_in_seconds))
        # Determine full hours
        hours = int(duration / 3600)
        # Determine full minutes of started hour
        minutes = int((duration - (hours * 3600)) / 60)
        # Determine full seconds of started minute
        seconds = int(duration - hours * 60 * 60 - minutes * 60)
        return '{:0>2d}:{:0>2d}:{:0>2d}'.format(hours, minutes, seconds)

    @staticmethod
    def format_bit_rate(bits_per_second: int) -> str:
        """
        Formats a bit rate in bits per second to make it human-readable.

        Parameters:
        bits_per_second (int): The bit rate in bits per second.

        Returns:
        str: A human-readable representation of the bit rate.
        """
        return '{} kb/s'.format(int(round(bits_per_second / 1000.0, 0)))

    @staticmethod
    def get_font_height(text: str, font: ImageFont.ImageFont) -> int:
        """
        Determine the height of a text using a specific font.

        Parameters:
        text (str): Text to render.
        font (ImageFont.ImageFont): Font to use for rendering the text.

        Returns:
        int: The height of the given text using the font.
        """
        bbox = font.getbbox(text)
        return int(bbox[3] - bbox[1]) + 1

class VideoThumbnailerException(Exception):
    """
    Exception of Python Video Thumbnailer.
    """

    def __init__(self, message: str):
        """
        Creates an exception specific for Python Video Thumbnailer.

        Parameters:
        message (str): The error message of this exception.
        """
        super().__init__(message)

class VideoThumbnailer:
    """
    Python Video Thumbnailer.
    """

    """
    The video file extensions that Python Video Thumbnailer recognized by default.
    """
    DEFAULT_VIDEO_EXTENSIONS = ('.avi',
                                '.divx',
                                '.flv',
                                '.m4v',
                                '.mkv',
                                '.mov',
                                '.mp4',
                                '.mpg',
                                '.wmv',
                                '.mts')

    def __init__(self):
        """
        Creates a new instance of Python Video Thumbnailer.
        """
        self.__init_parameters()

        # Take care of optional output directory
        if self.parameters.output_directory is not None:
            # If the directory does not yet exist, create it recursively
            if not self.parameters.output_directory.exists():
                try:
                    self.parameters.output_directory.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    message = 'Unable to create output directory \'{}\': {}'.format(self.parameters.output_directory.absolute(), e)
                    raise VideoThumbnailerException(message)
            # Exit if the path of the directory already exists, but is not a directory
            elif not self.parameters.output_directory.is_dir():
                message = 'Path of the output directory already exists and is not a directory: \'{}\''.format(self.parameters.output_directory.absolute())
                raise VideoThumbnailerException(message)

        self.__video_extensions = VideoThumbnailer.DEFAULT_VIDEO_EXTENSIONS

        # Font for the header texts
        self.__header_font = None
        if not self.parameters.no_header:
            if self.parameters.header_font_name is None:
                self.__header_font = ImageFont.load_default()
            else:
                self.__header_font = ImageFont.truetype(font=self.parameters.header_font_name, size=self.parameters.header_font_size)

    @staticmethod
    def __get_bool_store_action(b: bool) -> str:
        """
        Returns the store action string for the action parameter of ArgumentParser,
        which corresponds to the given boolean value.

        Parameters:
        b (bool): The boolean value.

        Returns:
        str: The store action for the boolean value, either 'store_true' or 'store_false'
        """
        if b:
            return 'store_true'
        return 'store_false'

    @staticmethod
    def __parse_args() -> Namespace:
        parser = ArgumentParser(description='Pyhton Video Thumbnailer. Command line tool for creating video preview thumbnails.')
        parser.add_argument('--width',
                             type=int,
                             help='The intended width of the preview thumbnails image in px. Actual width may be slightly less due rounding upon scaling.')
        parser.add_argument('--columns',
                             type=int,
                             help='The number of preview thumbnail columns.')
        parser.add_argument('--rows',
                             type=int,
                             help='The number of preview thumbnail rows.')
        parser.add_argument('--vertical-video-columns',
                             type=int,
                             help='The number of preview thumbnail columns in place of \'--columns\' in case of vertical videos.')
        parser.add_argument('--vertical-video-rows',
                             type=int,
                             help='The number of preview thumbnail rows in place of \'--rows\' in case of vertical videos.')
        parser.add_argument('--spacing',
                             type=int,
                             help='The spacing between and around the preview thumbnails in px.')
        parser.add_argument('--background-color',
                             type=str,
                             help="""Name or other definition of the PIL color to use for the image background,
                                    for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html""")
        parser.add_argument('--no-header',
                             action=VideoThumbnailer.__get_bool_store_action(not Parameters.DEFAULT_NO_HEADER),
                             help='Do not include a header with metadata and optional comment. Enabling this option will make all header settings irrelevant.')
        parser.add_argument('--header-font',
                             type=str,
                             help="""The name of a true type font to use for the header text providing information on the video file and its metadata.
                             If omitted, a built-in default font is used.""")
        parser.add_argument('--header-font-size',
                             type=int,
                             help='The font size of the header font, if a true type font is specified. With the built-in font, this value is ignored.')
        parser.add_argument('--header-font-color',
                             type=str,
                             help="""Name or other definition of the PIL color to use for the header font,
                             for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html""")
        parser.add_argument('--timestamp-font',
                             type=str,
                             help="""The name of a true type font to use for the preview thumbnail timestamps.
                             If omitted, a built-in default font is used.""")
        parser.add_argument('--timestamp-font-size',
                             type=int,
                             help='The font size of the timestamp font, if a true type font is specified. With the built-in font, this value is ignored.')
        parser.add_argument('--timestamp-font-color',
                             type=str,
                             help="""Name or other definition of the PIL color to use for the timestamp font,
                             for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html""")
        parser.add_argument('--timestamp-shadow-color',
                             type=str,
                             help="""Name or other definition of the PIL color to use for the shadow of the timestamps,
                                     for information on accepted values see https://pillow.readthedocs.io/en/stable/reference/ImageColor.html""")
        parser.add_argument('--comment-label',
                             type=str,
                             help="""Label used for an optional user-defined comment, which is added at the bottom of the video
                                     metadata information. If not defined, the default label 'Comment:' is used.""")
        parser.add_argument('--comment-text',
                             type=str,
                             help="""Text of an optional user-defined comment, which is added at the bottom of the video metadata information.
                                     If not defined, no comment is added and the respective text line is omitted in the header.""")
        parser.add_argument('--skip-seconds',
                             type=float,
                             help='The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail.')
        parser.add_argument('--suffix',
                             type=str,
                             help='An optional suffix to append to the file name of the generated preview thumbnails images.')
        parser.add_argument('--jpeg-quality',
                             type=int,
                             help='The quality of the JPEG image files that are created.')
        parser.add_argument('--override-existing',
                             action=VideoThumbnailer.__get_bool_store_action(not Parameters.DEFAULT_OVERRIDE_EXISTING),
                             help="""Override any existing image files, which have the same name as the generated images.
                             By default, a preview thumbnails image is not created, if the file to be created already exists.""")
        parser.add_argument('--recursive',
                             action=VideoThumbnailer.__get_bool_store_action(not Parameters.DEFAULT_RECURSIVE),
                             help='If creating preview thumbnails of video files in a directory, process subdirectories recursively.')
        parser.add_argument('--output-directory',
                             type=str,
                             help="""A directory, where all created preview thumbnails images should be saved.
                             If omitted, preview thumbnails images are saved in the same directory, where the respective video file is located.""")
        parser.add_argument('--raise-errors',
                             action=VideoThumbnailer.__get_bool_store_action(not Parameters.DEFAULT_RAISE_ERRORS),
                             help="""Stop if an error occurs by raising it. By default, errors are ignored and the affected preview thumbnails image is skipped.
                             This is useful, when processing multiple video files in a directory.""")
        parser.add_argument('--verbose',
                             action=VideoThumbnailer.__get_bool_store_action(not Parameters.DEFAULT_VERBOSE),
                             help='Print verbose information and messages.')
        parser.add_argument('filename',
                             nargs='?',
                             type=str,
                             help="""Video file of which to create preview thumbnails or directory, where multiple video files are located.
                             File name in the current working directory or path. If the argument is omitted, preview thumbnails are
                             generated for video files in the current working directory.""")
        return parser.parse_args()

    def __init_parameters(self):
        """
        Determines and returns the parameters to use for Python Video Thumbnailer.

        The parameters are initialized as follows:
        1. Built-in defaults
        2. Parameters defined in the configuration file .pyvideothumbnailer.conf,
           if found in the user's home directory
        3. Parameters supplied as command line arguments
        """
        # 1. Parameters, initialized with default values
        self.parameters = Parameters.from_defaults()

        # 2. Parameters from user-specific configuration file
        # Read the parameters, if the configuration file exists
        config_file = ConfigFile.get_config_file_path()
        if config_file.is_file():
            config = ConfigParser(allow_no_value=True)
            config.read(str(config_file.absolute()))
            if ConfigFile.CONFIG_SECTION_LAYOUT in config:
                layout_options = config.options(ConfigFile.CONFIG_SECTION_LAYOUT)
                if 'width' in layout_options:
                    self.parameters.width = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'width')
                if 'columns' in layout_options:
                    self.parameters.columns = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'columns')
                if 'rows' in layout_options:
                    self.parameters.rows = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'rows')
                if 'vertical_video_columns' in layout_options:
                    self.parameters.vertical_video_columns = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'vertical_video_columns')
                if 'vertical_video_rows' in layout_options:
                    self.parameters.vertical_video_rows = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'vertical_video_rows')
                if 'spacing' in layout_options:
                    self.parameters.spacing = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'spacing')
                if 'background_color' in layout_options:
                    color_value = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'background_color')
                    if color_value is not None and color_value != '':
                        self.parameters.background_color= ImageColor.getrgb(color_value)
                if 'no_header' in layout_options:
                    self.parameters.no_header = config.getboolean(ConfigFile.CONFIG_SECTION_LAYOUT, 'no_header')
                if 'header_font' in layout_options:
                    self.parameters.header_font_name = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'header_font')
                if 'header_font_size' in layout_options:
                    self.parameters.header_font_size = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'header_font_size')
                if 'header_font_color' in layout_options:
                    color_value = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'header_font_color')
                    if color_value is not None and color_value != '':
                        self.parameters.header_font_color = ImageColor.getrgb(color_value)
                if 'timestamp_font' in layout_options:
                    self.parameters.timestamp_font_name = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'timestamp_font')
                if 'timestamp_font_size' in layout_options:
                    self.parameters.timestamp_font_size = config.getint(ConfigFile.CONFIG_SECTION_LAYOUT, 'timestamp_font_size')
                if 'timestamp_font_color' in layout_options:
                    color_value = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'timestamp_font_color')
                    if color_value is not None and color_value != '':
                        self.parameters.timestamp_font_color = ImageColor.getrgb(color_value)
                if 'timestamp_shadow_color' in layout_options:
                    color_value = config.get(ConfigFile.CONFIG_SECTION_LAYOUT, 'timestamp_shadow_color')
                    if color_value is not None and color_value != '':
                        self.parameters.timestamp_shadow_color = ImageColor.getrgb(color_value)
                    else:
                        self.parameters.timestamp_shadow_color = None
            if ConfigFile.CONFIG_SECTION_HEADER in config:
                header_options = config.options(ConfigFile.CONFIG_SECTION_HEADER)
                if 'comment_label' in header_options:
                    self.parameters.comment_label = config.get(ConfigFile.CONFIG_SECTION_HEADER, 'comment_label')
                if 'comment_text' in header_options:
                    self.parameters.comment_text = config.get(ConfigFile.CONFIG_SECTION_HEADER, 'comment_text')
            if ConfigFile.CONFIG_SECTION_VIDEO in config:
                video_options = config.options(ConfigFile.CONFIG_SECTION_VIDEO)
                if 'skip_seconds' in video_options:
                    self.parameters.skip_seconds = config.getfloat(ConfigFile.CONFIG_SECTION_VIDEO, 'skip_seconds')
            if ConfigFile.CONFIG_SECTION_FILE in config:
                file_options = config.options(ConfigFile.CONFIG_SECTION_FILE)
                if 'recursive' in file_options:
                    self.parameters.recursive = config.getboolean(ConfigFile.CONFIG_SECTION_FILE, 'recursive')
                if 'suffix' in file_options:
                    self.parameters.suffix = config.get(ConfigFile.CONFIG_SECTION_FILE, 'suffix')
                if 'jpeg_quality' in file_options:
                    self.parameters.jpeg_quality = config.getint(ConfigFile.CONFIG_SECTION_FILE, 'jpeg_quality')
                if 'override_existing' in file_options:
                    self.parameters.override_existing = config.getboolean(ConfigFile.CONFIG_SECTION_FILE, 'override_existing')
                if 'output_directory' in file_options:
                    output_directory = config.get(ConfigFile.CONFIG_SECTION_FILE, 'output_directory')
                    if output_directory is not None:
                        self.parameters.output_directory = Path(output_directory)
            if ConfigFile.CONFIG_SECTION_PROGRAM in config:
                program_options = config.options(ConfigFile.CONFIG_SECTION_PROGRAM)
                if 'raise_errors' in program_options:
                    self.parameters.raise_errors = config.getboolean(ConfigFile.CONFIG_SECTION_PROGRAM, 'raise_errors')
                if 'verbose' in program_options:
                    self.parameters.verbose = config.getboolean(ConfigFile.CONFIG_SECTION_PROGRAM, 'verbose')

        # 3. Command line arguments
        # Override default parameters for arguments provided by the user
        args = VideoThumbnailer.__parse_args()
        if args.filename is not None:
            self.parameters.path = Path(args.filename)
        if args.recursive is not Parameters.DEFAULT_RECURSIVE:
            self.parameters.recursive = args.recursive
        if args.width is not None:
            self.parameters.width = args.width
        if args.columns is not None:
            self.parameters.columns = args.columns
        if args.rows is not None:
            self.parameters.rows = args.rows
        if args.vertical_video_columns is not None:
            self.parameters.vertical_video_columns = args.vertical_video_columns
        if args.vertical_video_rows is not None:
            self.parameters.vertical_video_rows = args.vertical_video_rows
        if args.spacing is not None:
            self.parameters.spacing = args.spacing
        if args.background_color is not None:
            self.parameters.background_color = ImageColor.getrgb(args.background_color)
        if args.no_header is not Parameters.DEFAULT_NO_HEADER:
            self.parameters.no_header = args.no_header
        if args.header_font is not None:
            self.parameters.header_font_name = args.header_font
        if args.header_font_size is not None:
            self.parameters.header_font_size = args.header_font_size
        if args.header_font_color is not None:
            self.parameters.header_font_color = ImageColor.getrgb(args.header_font_color)
        if args.timestamp_font is not None:
            self.parameters.timestamp_font_name = args.timestamp_font
        if args.timestamp_font_size is not None:
            self.parameters.timestamp_font_size = args.timestamp_font_size
        if args.timestamp_font_color is not None:
            self.parameters.timestamp_font_color = ImageColor.getrgb(args.timestamp_font_color)
        if args.timestamp_shadow_color is not None:
            self.parameters.timestamp_shadow_color = ImageColor.getrgb(args.timestamp_shadow_color)
        if args.comment_label is not None:
            self.parameters.comment_label = args.comment_label
        if args.comment_text is not None:
            self.parameters.comment_text = args.comment_text
        if args.skip_seconds is not None:
            self.parameters.skip_seconds = args.skip_seconds
        if args.suffix is not None:
            self.parameters.suffix = args.suffix
        if args.jpeg_quality is not None:
            self.parameters.jpeg_quality = args.jpeg_quality
        if args.override_existing is not Parameters.DEFAULT_OVERRIDE_EXISTING:
            self.parameters.override_existing = args.override_existing
        if args.output_directory is not None:
            self.parameters.output_directory = Path(args.output_directory)
        if args.raise_errors is not Parameters.DEFAULT_RAISE_ERRORS:
            self.parameters.raise_errors = args.raise_errors
        if args.verbose is not Parameters.DEFAULT_VERBOSE:
            self.parameters.verbose = args.verbose

    def add_video_extension(self, extension: str) -> None:
        """
        Adds a file extension to the list of video file extensions recognized by this
        Python Video Thumbnailer instance. Case of the extension does not matter as
        Python Video Thumbnailer recognizes file extensions in a case-insenstive way.
        The extension string should start with a '.'. If not, the dot is prepended.
        This method ensures that extensions are not added twice.

        Parameters:
        extension (str): The file extension to add to the list of recognized extensions.
        """
        if type(extension) != str:
            return
        extension = extension.lower()
        if not extension.startswidth('.'):
            extension = '.' + extension
        video_extensions = set(self.__video_extensions)
        video_extensions.add(extension)
        self.__video_extensions = tuple(video_extensions)

    def get_video_extensions(self) -> tuple:
        """
        Returns the video file extensions recognized by this Python Video Thumbnailer instance.

        Returns:
        tuple: The list of recognized file extensions.
        """
        return self.__video_extensions

    def set_video_extensions(self, extensions: list):
        """
        Sets the list of video file extensions recognized by this Python Video Thumbnailer instance.
        Case of the extension does not matter as Python Video Thumbnailer recognizes file extensions
        in a case-insenstive way. The extension string should start with a '.'. If not, the dot is
        prepended. This method ensures that extensions are not added twice.

        Parameters:
        extension (list): The list of recognized video file extension to set.
        """
        video_extensions = set()
        for extension in extensions:
            if type(extension) != str:
                continue
            extension = extension.lower()
            if not extension.startswidth('.'):
                extension = '.' + extension
            video_extensions.add(extension)
        self.__video_extensions = tuple(video_extensions)

    def create_and_save_preview_thumbnails_for(self, file_path: Path) -> None:
        """
        Creates preview thumbnails for a specified video file and save them to an image file
        according to the video file name and the directory and naming presets.

        Parameters:
        file_path (Path): The path of the video file, for which to create preview thumbnails.
        """
        # The path, where the created preview thumbnails image file should be saved.
        if self.parameters.suffix is None:
            self.parameters.suffix = ''
        image_path = None
        if self.parameters.output_directory is None:
            image_path = Path('{}{}.jpg'.format(file_path, self.parameters.suffix))
        else:
            image_path = self.parameters.output_directory / '{}{}.jpg'.format(file_path.name, self.parameters.suffix)

        if image_path.exists():
            if not self.parameters.override_existing:
                print('The path, where the preview image should be saved already exists, but shall not be overridden. Canceling creation of \'{}\'.'.format(image_path.absolute()), file=sys.stderr)
                return
            elif not image_path.is_file():
                print('The path, where the preview image should be saved already exists, but is not a file. Canceling creation of \'{}\'.'.format(image_path.absolute()), file=sys.stderr)
                return
            else:
                print('The file \'{}\' already exists and will be overridden as requested.'.format(image_path.absolute()))

        print('Creating preview thumbnails for \'{}\' ...'.format(file_path.absolute()))

        thumbnails_image = self.create_preview_thumbnails_for(file_path)

        # Save the preview thumbnails image
        if self.parameters.verbose:
            print('Saving preview thumbnails image to \'{}\''.format(image_path))
        thumbnails_image.save(image_path, quality=self.parameters.jpeg_quality)

        print('Done.')

    def create_preview_thumbnails_for(self, file_path: Path) -> Image:
        """
        Creates preview thumbnails for a specified video file and return the created in-memory image.

        Parameters:
        file_path (Path): The path of the video file, for which to create preview thumbnails.

        Returns:
        Image: A PIL image with the preview thumbnails.
        """

        # Open the video file.
        container = av.open(str(file_path))
        video_stream =  container.streams.video[0]

        # Parse the metadata from the video file
        # Dictionaries with general metadata, video metadata and audio metadata
        general_metadata = None
        video_metadata = None
        audio_metadata = None
        for track in MediaInfo.parse(file_path).tracks:
            # Dictionary with the track metadata
            metadata = track.to_data()

            if track.track_type == 'General' and general_metadata is None:
                general_metadata = metadata
            elif track.track_type == 'Video' and video_metadata is None:
                video_metadata = metadata
            elif track.track_type == 'Audio' and audio_metadata is None:
                audio_metadata = metadata
            else:
                continue

            if self.parameters.verbose:
                print('{} metadata:'.format(track.track_type))
                for key, value in sorted(metadata.items()):
                    print('{}: {}'.format(key, value))
                print()

        # General and video metadata information must be present
        if general_metadata is None:
            raise VideoThumbnailerException('Could not read general metadata from \'{}\'.'.format(file_path))
        if video_metadata is None:
            raise VideoThumbnailerException('Could not read video metadata from \'{}\'.'.format(file_path))

        # Width in px
        video_width = int(video_metadata['width'])
        # Height in px
        video_height = int(video_metadata['height'])
        # Aspect ratio
        video_aspect = float(video_width) / float(video_height)
        # Frames per second
        fps = float(video_metadata['frame_rate'])
        # Duration in seconds
        try:
            duration = float(video_metadata['duration']) / 1000.0
        except KeyError:
            raise VideoThumbnailerException('Video stream in \'{}\' has no duration set in metadata. Cannot calculate preview timestamps.'.format(file_path))

        # The number of preview thumbnail columns and rows
        columns = self.parameters.columns
        rows = self.parameters.rows
        # Use a different number of columns and rows in case of vertical videos, if requested
        if video_aspect < 1:
            if self.parameters.vertical_video_columns is not None:
                columns = self.parameters.vertical_video_columns
            if self.parameters.vertical_video_rows is not None:
                rows = self.parameters.vertical_video_rows

        # The number of thumbnail images to capture
        number_thumbnails = rows * columns
        if self.parameters.skip_seconds >= duration:
            print('Time to skip at the beginning ({} s) is longer than the duration of the video ({} s)!'.format(self.parameters.skip_seconds, duration), file=sys.stderr)
            return
        # The time step for iterating over the clip and capturing thumbnails
        time_step = (duration - self.parameters.skip_seconds) / number_thumbnails
        if time_step < 1.0 / fps:
            print('Video clip is too short to generate {} distinct preview thumbnails'.format(number_thumbnails), file=sys.stderr)
            return

        # Header for the preview thumbnails image providing file and metadata information
        # File information
        file_info = 'File: {}'.format(file_path.name)

        file_size = int(general_metadata['file_size'])
        size_info = None
        if file_size > 1024.0:
            size_info = 'Size: {} B ({}), Duration: {}'.format(file_size, Helper.format_size(file_size), Helper.format_time(duration))
        else:
            size_info = 'Size: {} B, Duration: {}'.format(file_size, Helper.format_time(duration))

        video_metadata['resolution'] = '{}x{}'.format(video_width, video_height)

        video_info = None
        for key in [ 'format', 'resolution', 'other_display_aspect_ratio', 'frame_rate', 'bit_rate' ]:
            try:
                value = video_metadata[key]
                if key == 'other_display_aspect_ratio':
                    value = '({})'.format(value[0])
                elif key == 'frame_rate':
                    value = '{:.2f} fps'.format(round(float(value), 2))
                elif key == 'bit_rate':
                    value = Helper.format_bit_rate(value)

                if video_info is None:
                    video_info = value
                elif key == 'other_display_aspect_ratio':
                    video_info += ' {}'.format(value)
                else:
                    video_info += ', {}'.format(value)
            except KeyError as e:
                if self.parameters.verbose:
                    print('Missing video metadata: {}'.format(e), file=sys.stderr)

        audio_info = None
        if audio_metadata is not None:
            for key in [ 'format', 'sampling_rate', 'channel_s', 'bit_rate']:
                try:
                    value = audio_metadata[key]
                    if key == 'sampling_rate':
                        value = '{} Hz'.format(value)
                    elif key == 'channel_s':
                        if value == 1:
                            value = 'mono'
                        elif value == 2:
                            value = 'stereo'
                        else:
                            value = '{} channels'.format(value)
                    elif key == 'bit_rate':
                        value = Helper.format_bit_rate(value)

                    if audio_info is None:
                        audio_info = value
                    else:
                        audio_info += ', {}'.format(value)
                except KeyError as e:
                    if self.parameters.verbose:
                        print('Missing audio metadata: {}'.format(e), file=sys.stderr)
        else:
            audio_info = 'None'

        video_info = 'Video: {}'.format(video_info)
        audio_info = 'Audio: {}'.format(audio_info)

        comment = None
        if self.parameters.comment_text is not None:
            comment_label = self.parameters.comment_label
            if not comment_label.endswith(':'):
                comment_label = '{}:'.format(comment_label)
            comment = '{} {}'.format(comment_label, self.parameters.comment_text)

        if self.parameters.verbose:
            print(file_info)
            print(size_info)
            print(video_info)
            print(audio_info)
            if comment is not None:
                print(comment)

        # Vertical (x) and horizontal (y) spacing between and around the preview thumbnails
        x_spacing = self.parameters.spacing
        y_spacing = self.parameters.spacing

        # Height of the header with the metadata
        header_height = 0
        if not self.parameters.no_header:
            # Spacing between the header text lines
            text_line_spacing = 2

            # Height of the header texts
            text_height_file_info = Helper.get_font_height(file_info, self.__header_font)
            text_height_size_info = Helper.get_font_height(size_info, self.__header_font)
            text_height_video_info = Helper.get_font_height(video_info, self.__header_font)
            text_height_audio_info = Helper.get_font_height(audio_info, self.__header_font)
            text_height_comment = 0
            if comment is not None:
                text_height_comment = Helper.get_font_height(comment, self.__header_font)

            # Compute the height of the header
            header_height = y_spacing
            header_height += text_height_file_info
            header_height += text_line_spacing
            header_height += text_height_size_info
            header_height += text_line_spacing
            header_height += text_height_video_info
            header_height += text_line_spacing
            header_height += text_height_audio_info
            if comment is not None:
                header_height += text_line_spacing
                header_height += text_height_comment

        # Width and height of the individual preview thumbnails
        thumbnail_width = float(self.parameters.width - x_spacing * (columns + 1)) / float(columns)
        thumbnail_height = int(thumbnail_width / video_aspect)
        thumbnail_width = int(thumbnail_width)
        # Recompute image width, because actual width of the preview thumbnails may be a few pixels less due to scaling and rounding to integer pixels
        image_width = thumbnail_width * columns + x_spacing * (columns + 1)
        image_height = header_height + thumbnail_height * rows + y_spacing * (rows + 1)

        if self.parameters.verbose:
            print('Image dimensions: {} x {} -> {} x {} thumbnails with dimensions {} x {}'.format(image_width, image_height, columns, rows, thumbnail_width, thumbnail_height))

        # PIL image for the preview thumbnails
        thumbnails_image = Image.new('RGB', (image_width, image_height), color=self.parameters.background_color)
        # PIL draw for adding text to the image
        thumbnails_draw = ImageDraw.Draw(thumbnails_image)

        # Drawing the header text
        if not self.parameters.no_header:
            x = x_spacing
            y = y_spacing
            thumbnails_draw.text((x, y), file_info, self.parameters.header_font_color, font=self.__header_font)
            y += text_height_file_info
            y += text_line_spacing
            thumbnails_draw.text((x, y), size_info, self.parameters.header_font_color, font=self.__header_font)
            y += text_height_size_info
            y += text_line_spacing
            thumbnails_draw.text((x, y), video_info, self.parameters.header_font_color, font=self.__header_font)
            y += text_height_video_info
            y += text_line_spacing
            thumbnails_draw.text((x, y), audio_info, self.parameters.header_font_color, font=self.__header_font)
            if comment is not None:
                y += text_height_comment
                y += text_line_spacing
                thumbnails_draw.text((x, y), comment, self.parameters.header_font_color, font=self.__header_font)

        # Font for timestamp texts
        timestamp_font = None
        if self.parameters.timestamp_font_name is None:
            timestamp_font = ImageFont.load_default()
        else:
            timestamp_font = ImageFont.truetype(font=self.parameters.timestamp_font_name, size=self.parameters.timestamp_font_size)
        x_spacing_timestamp = 2
        y_spacing_timestamp = 3
        timestamp_shadow_offset = 1

        # Video time at which to capture the next preview
        time = self.parameters.skip_seconds
        thumbnail_count = 0

        # Iterate over rows and columns creating and placing the preview thumbnails
        for row_index in range(rows):
            y = header_height + row_index * thumbnail_height + (row_index + 1) * y_spacing
            for column_index in range(columns):
                # https://programtalk.com/vs2/python/8441/PyAV/tests/test_seek.py/
                target_timestamp = int(time / video_stream.time_base) + video_stream.start_time
                # Seeks to the frame at target_timestamp if it is a keyframe or the last keyframe before
                container.seek(target_timestamp, stream=video_stream)
                x = column_index * thumbnail_width + (column_index + 1) * x_spacing
                # Capture, resize and position a preview thumbnail
                frame_captured = False
                for packet in container.demux(video_stream):
                    for frame in packet.decode():
                        # pts = presentation timestamp in time_base units
                        if frame.pts >= target_timestamp:
                            # VideoFrame.to_image() returns a PIL image
                            image = frame.to_image().resize((thumbnail_width, thumbnail_height))
                            thumbnails_image.paste(image, box=(x, y))
                            frame_captured = True
                            break
                    if frame_captured:
                        break

                # Add a human-readable timestamp to the preview thumbnail
                formatted_time = Helper.format_time(time)
                timestamp_width = timestamp_font.getlength(formatted_time)
                timestamp_height = Helper.get_font_height(formatted_time, timestamp_font)
                x_timestamp = x + thumbnail_width - timestamp_width - x_spacing_timestamp
                y_timestamp = y + thumbnail_height - timestamp_height - y_spacing_timestamp - timestamp_shadow_offset
                timestamp_position = (x_timestamp, y_timestamp)
                shadow_position = (x_timestamp + timestamp_shadow_offset, y_timestamp + timestamp_shadow_offset)
                # Black timestamp 'shadow'
                if self.parameters.timestamp_shadow_color is not None:
                    thumbnails_draw.text(shadow_position, formatted_time, self.parameters.timestamp_shadow_color, font=timestamp_font)
                # White timestamp text
                thumbnails_draw.text(timestamp_position, formatted_time, self.parameters.timestamp_font_color, font=timestamp_font)

                thumbnail_count += 1
                if self.parameters.verbose:
                    print('Captured preview thumbnail #{} of frame at {:.3f} s'.format(thumbnail_count, time))
                time += time_step

        # Close the video clip
        container.close()
        return thumbnails_image

    def has_recognized_video_extension(self, file_name: str) -> bool:
        """
        Checks if a file name ends with a recognized video file extension.

        Checks if the provided file name ends with an extension that is recognized by this instance
        of Python Video Thumbnailer. The check is case-insensitive.

        Parameters:
        file_name (str): The file name to check.

        Returns:
        bool: True if the file name ends with one of the recognized video extensions, False otherwise.
        """
        return file_name.lower().endswith(self.__video_extensions)

    def process_file_or_directory(self, path: Path) -> None:
        """
        Process a file or directory and create preview thumbnails of identified video files.

        If called on a file, preview thumbnails are created if the file is a video.
        If called on a directory, preview thumbnails are created of video files found in the directory.
        This is done in a recursive way, if recursion is enabled in the parameters.

        Parameters:
        path (Path): The path of the video file to process or the path of the directory, in which to process video files.
        """
        # List of files and directories to process
        paths_to_process = None
        # If the path is a directory, list its contents
        if path.is_dir():
            if not os.access(path, os.X_OK | os.W_OK):
                print('Cannot consider directory \'{}\'. Permission for writing files to it is denied.'.format(path.absolute()))
                return
            paths_to_process = sorted(path.iterdir())
        # If the path is a file
        elif path.is_file():
            if not os.access(path, os.R_OK):
                print('Cannot consider video file \'{}\'. Permission for reading it is denied.'.format(path.absolute()))
                return
            if not os.access(path.parent, os.X_OK | os.W_OK):
                print('Cannot consider video file \'{}\'. Permission for writing files to its directory \'{}\' is denied.'.format(path.name, path.parent.absolute()))
                return
            # Path of the file (as sole element in a list to be compatible with iteration below)
            paths_to_process = [path]
        else:
            print('Path \'{}\' is neither a file nor a directory.'.format(path.absolute()))
            return

        # If path is a directory, iterate over the contained files and directories.
        # If path is a file, just 'iterate' over this single file.
        for path in paths_to_process:
            # If recursive, call the process method on any subdirectories
            if self.parameters.recursive and path.is_dir():
                self.process_file_or_directory(path)
            # Create preview thumbnails of (potential) video files
            elif path.is_file() and self.has_recognized_video_extension(path.name):
                try:
                    self.create_and_save_preview_thumbnails_for(path)
                except Exception as e:
                    if self.parameters.raise_errors:
                        raise e
                    else:
                        print('An error occurred:\n{}\nSkipping file \'{}\'.'.format(e, path.absolute()), file=sys.stderr)

    def create_and_save_preview_thumbnails(self):
        """
        Starts creating preview thumbnails of the specified file, in the specified directory or
        in the current directory.
        """
        self.process_file_or_directory(self.parameters.path)

def main():
    try:
        video_thumbnailer = VideoThumbnailer()
    except VideoThumbnailerException as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    video_thumbnailer.create_and_save_preview_thumbnails()

if __name__ == '__main__':
    main()
