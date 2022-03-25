#!/usr/bin/python3

from __future__ import annotations

import os
import sys

from argparse import ArgumentParser
from argparse import Namespace

from configparser import ConfigParser

# Library for accessing metadata and other media information (https://github.com/sbraz/pymediainfo)
from pymediainfo import MediaInfo

# Library for video editing (https://github.com/Zulko/moviepy)
from moviepy.editor import VideoFileClip

# Python imaging library (https://python-pillow.org/)
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

CONFIG_FILE_NAME = '.pyvideothumbnailer.conf'

VIDEO_EXTENSIONS = ('.avi',
                    '.divx',
                    '.flv',
                    '.m4v',
                    '.mkv',
                    '.mov',
                    '.mp4',
                    '.mpg',
                    '.wmv')

DEFAULT_PATH = os.getcwd()
DEFAULT_RECURSIVE = False
DEFAULT_WIDTH = 800
DEFAULT_COLUMNS = 4
DEFAULT_ROWS = 3
DEFAULT_VERTICAL_VIDEO_COLUMNS = None
DEFAULT_VERTICAL_VIDEO_ROWS = None
DEFAULT_SPACING = 2
DEFAULT_BACKGROUND_COLOR = 'white'
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

CONFIG_SECTION_LAYOUT = 'Layout'
CONFIG_SECTION_HEADER = 'Header'
CONFIG_SECTION_VIDEO = 'Video'
CONFIG_SECTION_FILE = 'File'
CONFIG_SECTION_PROGRAM = 'Program'

class PyVideoThumbnailerParameters:

    def __init__(self, path: str, recursive: bool, width: int, columns: int, rows: int,
                 vertical_video_columns: int, vertical_video_rows: int, spacing: int,
                 background_color: str, header_font_name: str, header_font_size: int, header_font_color: str,
                 timestamp_font_name: str, timestamp_font_size: int, timestamp_font_color: str, timestamp_shadow_color: str,
                 comment_label: str, comment_text: str,
                 skip_seconds: float, suffix: str, jpeg_quality: int, override_existing: bool, output_directory_path: str,
                 raise_errors: bool, verbose: bool):
        """
        Constructor for an instance of the object holding all of the parameters of Python Video Thumbnailer.

        Parameters:
        path (str): The path of the video file of which to create a preview thumbnails image
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
        output_directory_path (str): A directory, where all created preview thumbnails images should be saved.
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
        self.output_directory_path = output_directory_path
        self.raise_errors = raise_errors
        self.verbose = verbose

    @staticmethod
    def from_defaults() -> PyVideoThumbnailerParameters.PyVideoThumbnailerParameters:
        return PyVideoThumbnailerParameters(DEFAULT_PATH,
                                            DEFAULT_RECURSIVE,
                                            DEFAULT_WIDTH,
                                            DEFAULT_COLUMNS,
                                            DEFAULT_ROWS,
                                            DEFAULT_VERTICAL_VIDEO_COLUMNS,
                                            DEFAULT_VERTICAL_VIDEO_ROWS,
                                            DEFAULT_SPACING,
                                            DEFAULT_BACKGROUND_COLOR,
                                            DEFAULT_HEADER_FONT_NAME,
                                            DEFAULT_HEADER_FONT_SIZE,
                                            DEFAULT_HEADER_FONT_COLOR,
                                            DEFAULT_TIMESTAMP_FONT_NAME,
                                            DEFAULT_TIMESTAMP_FONT_SIZE,
                                            DEFAULT_TIMESTAMP_FONT_COLOR,
                                            DEFAULT_TIMESTAMP_SHADOW_COLOR,
                                            DEFAULT_COMMENT_LABEL,
                                            DEFAULT_COMMENT_TEXT,
                                            DEFAULT_SKIP_SECONDS,
                                            DEFAULT_SUFFIX,
                                            DEFAULT_JPEG_QUALITY,
                                            DEFAULT_OVERRIDE_EXISTING,
                                            DEFAULT_OUTPUT_DIRECTORY,
                                            DEFAULT_RAISE_ERRORS,
                                            DEFAULT_VERBOSE)

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

def format_time(duration_in_seconds: float) -> str:
    """
    Formats a duration in seconds to make it human-readable.

    Parameters:
    duration_in_seconds (float): The duration in seconds.

    Returns:
    str: A human-readable representation of the duration.
    """
    # Cast duration to full seconds
    duration = int(duration_in_seconds)
    # Determine full hours
    hours = int(duration / 3600)
    # Determine full minutes of started hour
    minutes = int((duration - (hours * 3600)) / 60)
    # Determine full seconds of started minute
    seconds = int(duration - hours * 60 * 60 - minutes * 60)
    return '{:0>2d}:{:0>2d}:{:0>2d}'.format(hours, minutes, seconds)

def format_bit_rate(bits_per_second: int) -> str:
    """
    Formats a bit rate in bits per second to make it human-readable.

    Parameters:
    bits_per_second (int): The bit rate in bits per second.

    Returns:
    str: A human-readable representation of the bit rate.
    """
    return '{} kb/s'.format(int(round(bits_per_second / 1000.0, 0)))

def create_preview_thumbnails(params: PyVideoThumbnailerParameters, file_path: str) -> None:
    """
    Create preview thumbnails of a video file.

    Parameters:
    params (PyVideoThumbnailerParameters): The parameters that control, which preview thumbnails images are created
                                           and their properties.
    file_path (str): The path of the video file of which to create thumbnails.
    """
    # The path, where the created preview thumbnails image file should be saved.
    if params.suffix is None:
        params.suffix = ''
    image_path = None
    if params.output_directory_path is None:
        image_path = '{}{}.jpg'.format(file_path, params.suffix)
    else:
        image_path = os.path.join(params.output_directory_path, '{}{}.jpg'.format(os.path.basename(file_path), params.suffix))

    if os.path.exists(image_path):
        if not params.override_existing:
            print('The path, where the preview image should be saved already exists, but shall not be overridden. Canceling creation of \'{}\'.'.format(os.path.abspath(image_path)), file=sys.stderr)
            return
        elif not os.path.isfile(image_path):
            print('The path, where the preview image should be saved already exists, but is not a file. Canceling creation of \'{}\'.'.format(os.path.abspath(image_path)), file=sys.stderr)
            return
        else:
            print('The file \'{}\' already exists and will be overridden as requested.'.format(os.path.abspath(image_path)))

    print('Creating preview thumbnails for \'{}\' ...'.format(os.path.abspath(file_path)))

    # Open the video file. Raises an IOError if the file is not a video.
    video_clip = VideoFileClip(file_path)

    # Width in px
    video_width = video_clip.w
    # Height in px
    video_height = video_clip.h
    # Aspect ratio
    video_aspect = float(video_width) / float(video_height)
    # Number of frames
    number_frames = video_clip.reader.nframes
    # Frames per second
    fps = video_clip.fps
    # Duration in seconds
    duration = video_clip.duration

    # The number of preview thumbnail columns and rows
    columns = params.columns
    rows = params.rows
    # Use a different number of columns and rows in case of vertical videos, if requested
    if video_aspect < 1:
        if params.vertical_video_columns is not None:
            columns = params.vertical_video_columns
        if params.vertical_video_rows is not None:
            rows = params.vertical_video_rows

    # The number of thumbnail images to capture
    number_thumbnails = rows * columns
    if params.skip_seconds >= duration:
        print('Time to skip at the beginning ({} s) is longer than the duration of the video ({} s)!'.format(params.skip_seconds, duration), file=sys.stderr)
        return
    # The time step for iterating over the clip and capturing thumbnails
    time_step = (duration - params.skip_seconds) / number_thumbnails
    if time_step < 1.0 / fps:
        print('Video clip ({} frames) is too short to generate {} distinct preview thumbnails'.format(number_frames, number_thumbnails), file=sys.stderr)
        return

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

        if params.verbose:
            for key, value in metadata.items():
                print('{}: {}'.format(key, value))
            print()

    # Header for the preview thumbnails image providing file and metadata information
    # File information
    file_info = 'File: {}'.format(os.path.basename(file_path))

    file_size = int(general_metadata['file_size'])
    size_info = None
    if file_size > 1024.0:
        size_info = 'Size: {} B ({}), Duration: {}'.format(file_size, format_size(file_size), format_time(duration))
    else:
        size_info = 'Size: {} B, Duration: {}'.format(file_size, format_time(duration))

    # Video metadata information
    if video_metadata is None:
        return

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
                value = format_bit_rate(value)

            if video_info is None:
                video_info = value
            elif key == 'other_display_aspect_ratio':
                video_info += ' {}'.format(value)
            else:
                video_info += ', {}'.format(value)
        except KeyError as e:
            if params.verbose:
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
                    value = format_bit_rate(value)

                if audio_info is None:
                    audio_info = value
                else:
                    audio_info += ', {}'.format(value)
            except KeyError as e:
                if params.verbose:
                    print('Missing audio metadata: {}'.format(e), file=sys.stderr)
    else:
        audio_info = 'None'

    video_info = 'Video: {}'.format(video_info)
    audio_info = 'Audio: {}'.format(audio_info)

    comment = None
    if params.comment_text is not None:
        comment_label = params.comment_label
        if not comment_label.endswith(':'):
            comment_label = '{}:'.format(comment_label)
        comment = '{} {}'.format(comment_label, params.comment_text)

    if params.verbose:
        print(file_info)
        print(size_info)
        print(video_info)
        print(audio_info)
        if comment is not None:
            print(comment)

    # Vertical (x) and horizontal (y) spacing between and around the preview thumbnails
    x_spacing = params.spacing
    y_spacing = params.spacing

    # Spacing between the header text lines
    text_line_spacing = 2
    # Font for the header texts
    header_font = None
    if params.header_font_name is None:
        header_font = ImageFont.load_default()
    else:
        header_font = ImageFont.truetype(font=params.header_font_name, size=params.header_font_size)

    # Height of the header texts
    text_height_file_info = header_font.getsize(file_info)[1]
    text_height_size_info = header_font.getsize(size_info)[1]
    text_height_video_info = header_font.getsize(video_info)[1]
    text_height_audio_info = header_font.getsize(audio_info)[1]
    text_height_comment = 0
    if comment is not None:
        text_height_comment = header_font.getsize(comment)[1]

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
    thumbnail_width = float(params.width - x_spacing * (columns + 1)) / float(columns)
    thumbnail_height = int(thumbnail_width / video_aspect)
    thumbnail_width = int(thumbnail_width)
    # Recompute image width, because actual width of the preview thumbnails may be a few pixels less due to scaling and rounding to integer pixels
    image_width = thumbnail_width * columns + x_spacing * (columns + 1)
    image_height = header_height + thumbnail_height * rows + y_spacing * (rows + 1)

    if params.verbose:
        print('Image dimensions: {} x {} -> {} x {} thumbnails with dimensions {} x {}'.format(image_width, image_height, columns, rows, thumbnail_width, thumbnail_height))

    # PIL image for the preview thumbnails
    thumbnails_image = Image.new('RGB', (image_width, image_height), color=params.background_color)
    # PIL draw for adding text to the image
    thumbnails_draw = ImageDraw.Draw(thumbnails_image)

    # Drawing the header text
    x = x_spacing
    y = y_spacing
    thumbnails_draw.text((x, y), file_info, params.header_font_color, font=header_font)
    y += text_height_file_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), size_info, params.header_font_color, font=header_font)
    y += text_height_size_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), video_info, params.header_font_color, font=header_font)
    y += text_height_video_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), audio_info, params.header_font_color, font=header_font)
    if comment is not None:
        y += text_height_comment
        y += text_line_spacing
        thumbnails_draw.text((x, y), comment, params.header_font_color, font=header_font)

    # Font for timestamp texts
    timestamp_font = None
    if params.timestamp_font_name is None:
        timestamp_font = ImageFont.load_default()
    else:
        timestamp_font = ImageFont.truetype(font=params.timestamp_font_name, size=params.timestamp_font_size)
    x_spacing_timestamp = 2
    y_spacing_timestamp = 2
    timestamp_shadow_offset = 1

    # Video time at which to capture the next preview
    time = params.skip_seconds
    thumbnail_count = 0

    # Iterate over rows and columns creating and placing the preview thumbnails
    for row_index in range(rows):
        y = header_height + row_index * thumbnail_height + (row_index + 1) * y_spacing
        for column_index in range(columns):
            x = column_index * thumbnail_width + (column_index + 1) * x_spacing
            # Capture, resize and position a preview thumbnail
            frame = video_clip.get_frame(time)
            image = Image.fromarray(frame)
            image.thumbnail((thumbnail_width, thumbnail_height))
            thumbnails_image.paste(image, box=(x, y))

            # Add a human-readable timestamp to the preview thumbnail
            formatted_time = format_time(time)
            timestamp_size = timestamp_font.getsize(formatted_time)
            timestamp_width = timestamp_size[0]
            timestamp_height = timestamp_size[1]
            x_timestamp = x + thumbnail_width - timestamp_width - x_spacing_timestamp
            y_timestamp = y + thumbnail_height - timestamp_height - y_spacing_timestamp - timestamp_shadow_offset
            timestamp_position = (x_timestamp, y_timestamp)
            shadow_position = (x_timestamp + timestamp_shadow_offset, y_timestamp + timestamp_shadow_offset)
            # Black timestamp 'shadow'
            if params.timestamp_shadow_color is not None:
                thumbnails_draw.text(shadow_position, formatted_time, params.timestamp_shadow_color, font=timestamp_font)
            # White timestamp text
            thumbnails_draw.text(timestamp_position, formatted_time, params.timestamp_font_color, font=timestamp_font)

            thumbnail_count += 1
            if params.verbose:
                print('Captured preview thumbnail #{} of frame at {:.3f} s'.format(thumbnail_count, time))
            time += time_step

    # Save the preview thumbnails image
    if params.verbose:
        print('Saving preview thumbnails image to \'{}\''.format(image_path))
    thumbnails_image.save(image_path, quality=params.jpeg_quality)

    # Close the video clip
    video_clip.close()
    print('Done.')

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

def process_file_or_directory(params: PyVideoThumbnailerParameters) -> None:
    """
    Process a file or directory and create preview thumbnails of identified video files.

    If called on a file, preview thumbnails are created if the file is a video.
    If called on a directory, preview thumbnails are created of video files found in the directory.

    Parameters:
    params (PyVideoThumbnailerParameters): The parameters that control, which preview thumbnails images are created
                                           and their properties.
    """
    # List of files and directories to process
    file_names = None
    # If the path is a directory, list its contents
    if os.path.isdir(params.path):
        file_names = sorted(os.listdir(params.path))
    # If the path is a file, get its dirname and basename
    elif os.path.isfile(params.path):
        path_elements = os.path.split(params.path)
        # dirname
        params.path = path_elements[0]
        # basename (as sole element in a list to be compatible with iteration below)
        file_names = [path_elements[1]]
    else:
        print('Path \'{}\' is neither a file nor a directory.'.format(os.path.abspath(params.path)))
        return

    # If path is a directory, iterate over the contained files and directories.
    # If path is a file, just 'iterate' over this single file.
    for file_name in file_names:
        file_path = os.path.join(params.path, file_name)
        # If recursive, call the process method on any subdirectories
        if params.recursive and os.path.isdir(file_path):
            process_file_or_directory(file_path, True)
        # Create preview thumbnails of (potential) video files
        elif os.path.isfile(file_path) and has_video_extension(file_name):
            try:
                create_preview_thumbnails(params, file_path)
            except Exception as e:
                if params.raise_errors:
                    raise e
                else:
                    print('An error occurred:\n{}\nSkipping file \'{}\'.'.format(e, os.path.abspath(file_path)), file=sys.stderr)

def parse_args() -> Namespace:
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
    parser.add_argument('---vertical-video-columns',
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
                         action='store_true',
                         help="""Override any existing image files, which have the same name as the generated images.
                         By default, a preview thumbnails image is not created, if the file to be created already exists.""")
    parser.add_argument('--recursive',
                         action='store_true',
                         help='If creating preview thumbnails of video files in a directory, process subdirectories recursively.')
    parser.add_argument('--output-directory',
                         type=str,
                         help="""A directory, where all created preview thumbnails images should be saved.
                         If omitted, preview thumbnails images are saved in the same directory, where the respective video file is located.""")
    parser.add_argument('--raise-errors',
                         action='store_true',
                         help="""Stop if an error occurs by raising it. By default, errors are ignored and the affected preview thumbnails image is skipped.
                         This is useful, when processing multiple video files in a directory.""")
    parser.add_argument('--verbose',
                         action='store_true',
                         help='Print verbose information and messages.')
    parser.add_argument('filename',
                         nargs='?',
                         type=str,
                         help="""Video file of which to create preview thumbnails or directory, where multiple video files are located.
                         File name in the current working directory or path. If the argument is omitted, preview thumbnails are
                         generated for video files in the current working directory.""")
    return parser.parse_args()

def get_parameters() -> PyVideoThumbnailerParameters:
    """
    Determines and returns the parameters to use for Python Video Thumbnailer.

    The parameters are initialized as follows:
    1. Built-in defaults
    2. Parameters defined in the configuration file .pyvideothumbnailer.conf,
       if found in the user's home directory
    3. Parameters supplied as command line arguments

    Returns:
    PyVideoThumbnailerParameters: The parameters that control, which preview thumbnails images are created
                                  and their properties
    """
    # 1. Parameters, initialized with default values
    params = PyVideoThumbnailerParameters.from_defaults()

    # 2. Parameters from user-specific configuration file
    # Read the parameters, if the configuration file exists
    user_home = os.path.expanduser('~')
    config_file = os.path.join(user_home, CONFIG_FILE_NAME)
    if os.path.isfile(config_file):
        config = ConfigParser(allow_no_value=True)
        config.read(config_file)
        if CONFIG_SECTION_LAYOUT in config:
            layout_options = config.options(CONFIG_SECTION_LAYOUT)
            if 'width' in layout_options:
                params.width = config.getint(CONFIG_SECTION_LAYOUT, 'width')
            if 'columns' in layout_options:
                params.columns = config.getint(CONFIG_SECTION_LAYOUT, 'columns')
            if 'rows' in layout_options:
                params.rows = config.getint(CONFIG_SECTION_LAYOUT, 'rows')
            if 'vertical_video_columns' in layout_options:
                params.vertical_video_columns = config.getint(CONFIG_SECTION_LAYOUT, 'vertical_video_columns')
            if 'vertical_video_rows' in layout_options:
                params.vertical_video_rows = config.getint(CONFIG_SECTION_LAYOUT, 'vertical_video_rows')
            if 'spacing' in layout_options:
                params.spacing = config.getint(CONFIG_SECTION_LAYOUT, 'spacing')
            if 'header_font' in layout_options:
                params.header_font_name = config.get(CONFIG_SECTION_LAYOUT, 'header_font')
            if 'header_font_size' in layout_options:
                params.header_font_size = config.getint(CONFIG_SECTION_LAYOUT, 'header_font_size')
            if 'header_font_color' in layout_options:
                color_value = config.get(CONFIG_SECTION_LAYOUT, 'header_font_color')
                if color_value is not None and color_value != '':
                    params.header_font_color = ImageColor.getrgb(color_value)
            if 'timestamp_font' in layout_options:
                params.timestamp_font_name = config.get(CONFIG_SECTION_LAYOUT, 'timestamp_font')
            if 'timestamp_font_size' in layout_options:
                params.timestamp_font_size = config.getint(CONFIG_SECTION_LAYOUT, 'timestamp_font_size')
            if 'timestamp_font_color' in layout_options:
                color_value = config.get(CONFIG_SECTION_LAYOUT, 'timestamp_font_color')
                if color_value is not None and color_value != '':
                    params.timestamp_font_color = ImageColor.getrgb(color_value)
            if 'timestamp_shadow_color' in layout_options:
                color_value = config.get(CONFIG_SECTION_LAYOUT, 'timestamp_shadow_color')
                if color_value is not None and color_value != '':
                    params.timestamp_shadow_color = ImageColor.getrgb(color_value)
                else:
                    params.timestamp_shadow_color = None
        if CONFIG_SECTION_HEADER in config:
            header_options = config.options(CONFIG_SECTION_HEADER)
            if 'comment_label' in header_options:
                params.comment_label = config.get(CONFIG_SECTION_HEADER, 'comment_label')
            if 'comment_text' in header_options:
                params.comment_text = config.get(CONFIG_SECTION_HEADER, 'comment_text')
        if CONFIG_SECTION_VIDEO in config:
            video_options = config.options(CONFIG_SECTION_VIDEO)
            if 'skip_seconds' in video_options:
                params.skip_seconds = config.getfloat(CONFIG_SECTION_VIDEO, 'skip_seconds')
        if CONFIG_SECTION_FILE in config:
            file_options = config.options(CONFIG_SECTION_FILE)
            if 'recursive' in file_options:
                params.recursive = config.getboolean(CONFIG_SECTION_FILE, 'recursive')
            if 'suffix' in file_options:
                params.suffix = config.get(CONFIG_SECTION_FILE, 'suffix')
            if 'jpeg_quality' in file_options:
                params.jpeg_quality = config.getint(CONFIG_SECTION_FILE, 'jpeg_quality')
            if 'override_existing' in file_options:
                params.override_existing = config.getboolean(CONFIG_SECTION_FILE, 'override_existing')
            if 'output_directory' in file_options:
                params.output_directory = config.get(CONFIG_SECTION_FILE, 'output_directory')
        if CONFIG_SECTION_PROGRAM in config:
            program_options = config.options(CONFIG_SECTION_PROGRAM)
            if 'raise_errors' in program_options:
                params.raise_errors = config.getboolean(CONFIG_SECTION_PROGRAM, 'raise_errors')
            if 'verbose' in program_options:
                params.verbose = config.getboolean(CONFIG_SECTION_PROGRAM, 'verbose')

    # 3. Command line arguments
    # Override default parameters for arguments provided by the user
    args = parse_args()
    if args.filename is not None:
        params.path = args.filename
    if args.recursive is not False:
        params.recursive = args.recursive
    if args.width is not None:
        params.width = args.width
    if args.columns is not None:
        params.columns = args.columns
    if args.rows is not None:
        params.rows = args.rows
    if args.vertical_video_columns is not None:
        params.vertical_video_columns = args.vertical_video_columns
    if args.vertical_video_rows is not None:
        params.vertical_video_rows = args.vertical_video_rows
    if args.spacing is not None:
        params.spacing = args.spacing
    if args.background_color is not None:
        params.background_color = ImageColor.getrgb(args.background_color)
    if args.header_font is not None:
        params.header_font_name = args.header_font
    if args.header_font_size is not None:
        params.header_font_size = args.header_font_size
    if args.header_font_color is not None:
        params.header_font_color = ImageColor.getrgb(args.header_font_color)
    if args.timestamp_font is not None:
        params.timestamp_font_name = args.timestamp_font
    if args.timestamp_font_size is not None:
        params.timestamp_font_size = args.timestamp_font_size
    if args.timestamp_font_color is not None:
        params.timestamp_font_color = ImageColor.getrgb(args.timestamp_font_color)
    if args.timestamp_shadow_color is not None:
        params.timestamp_shadow_color = ImageColor.getrgb(args.timestamp_shadow_color)
    if args.comment_label is not None:
        params.comment_label = args.comment_label
    if args.comment_text is not None:
        params.comment_text = args.comment_text
    if args.skip_seconds is not None:
        params.skip_seconds = args.skip_seconds
    if args.suffix is not None:
        params.suffix = args.suffix
    if args.jpeg_quality is not None:
        params.jpeg_quality = args.jpeg_quality
    if args.override_existing is not False:
        params.override_existing = args.override_existing
    if args.output_directory is not None:
        params.output_directory_path = args.output_directory
    if args.raise_errors is not False:
        params.raise_errors = args.raise_errors
    if args.verbose is not None:
        params.verbose = args.verbose

    return params

if __name__ == '__main__':
    # Get the parameters
    params = get_parameters()

    # Take care of optional output directory
    if params.output_directory_path is not None:
        # If the directory does not yet exist, create it recursively
        if not os.path.exists(params.output_directory_path):
            try:
                os.makedirs(params.output_directory_path)
            except Exception as e:
                print('Unable to create output directory \'{}\': {}'.format(os.path.abspath(params.output_directory_path), e), file=sys.stderr)
                sys.exit(1)
        # Exit if the path of the directory already exists, but is not a directory
        elif not os.path.isdir(params.output_directory):
            print('Path of the output directory already exists and is not a directory: \'{}\''.format(os.path.abspath(params.output_directory_path)), file=sys.stderr)
            sys.exit(1)

    # Process preview thumbnails image creation
    process_file_or_directory(params)
