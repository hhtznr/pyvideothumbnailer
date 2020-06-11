#!/usr/bin/python3

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from argparse import Namespace

# Library for accessing metadata and other media information (https://github.com/sbraz/pymediainfo)
from pymediainfo import MediaInfo

# Library for video editing (https://github.com/Zulko/moviepy)
from moviepy.editor import VideoFileClip

# Python imaging library (https://python-pillow.org/)
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

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

DEFAULT_WIDTH = 800
DEFAULT_COLUMNS = 4
DEFAULT_ROWS = 3
DEFAULT_SPACING = 2
DEFAULT_SKIP_SECONDS = 10.0
DEFAULT_JPEG_QUALITY = 95

PIL_COLOR_BLACK = ImageColor.getrgb('black')
PIL_COLOR_WHITE = ImageColor.getrgb('white')

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
    minutes = int((duration - hours * 60) / 60)
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

def create_preview_thumbnails(file_path: str, width: int, columns: int, rows: int, spacing: int,
                              skip_seconds: float, jpeg_quality: int, verbose: bool) -> None:
    """
    Create preview thumbnails of a video file.

    Parameters:
    file_path (str): The path of the video file of which to create thumbnails.
    width (int): The width in pixels of the created preview thumbnails image.
    columns (int): The number of thumbnail columns.
    rows (int): The number of thumbnail rows.
    spacing (int): The spacing in pixels between and around the preview thumbnails.
    skip_seconds (float): The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail.
    jpeg_quality (int): The quality of the JPEG image file that is created.
    verbose (bool): Print verbose information and messages.
    """
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

    # The number of thumbnail images to capture
    number_thumbnails = rows * columns
    if skip_seconds >= duration:
        print('Time to skip at the beginning ({} s) is longer than the duration of the video ({} s)!'.format(skip_seconds, duration), file=sys.stderr)
        return
    # The time step for iterating over the clip and capturing thumbnails
    time_step = (duration - skip_seconds) / number_thumbnails
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

        if verbose:
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
            if verbose:
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
                if verbose:
                    print('Missing audio metadata: {}'.format(e), file=sys.stderr)
    else:
        audio_info = 'None'

    video_info = 'Video: {}'.format(video_info)
    audio_info = 'Audio: {}'.format(audio_info)

    if verbose:
        print(file_info)
        print(size_info)
        print(video_info)
        print(audio_info)

    # Vertical (x) and horizontal (y) spacing between and around the preview thumbnails
    x_spacing = spacing
    y_spacing = spacing

    # Spacing between the header text lines
    text_line_spacing = 2
    # Font for the header texts
    header_font = ImageFont.load_default()

    # Height of the header texts
    text_height_file_info = header_font.getsize(file_info)[1]
    text_height_size_info = header_font.getsize(size_info)[1]
    text_height_video_info = header_font.getsize(video_info)[1]
    text_height_audio_info = header_font.getsize(audio_info)[1]

    # Compute the height of the header
    header_height = y_spacing
    header_height += text_height_file_info
    header_height += text_line_spacing
    header_height += text_height_size_info
    header_height += text_line_spacing
    header_height += text_height_video_info
    header_height += text_line_spacing
    header_height += text_height_audio_info

    # Width and height of the individual preview thumbnails
    thumbnail_width = float(width - x_spacing * (columns + 1)) / float(columns)
    thumbnail_height = int(thumbnail_width / video_aspect)
    thumbnail_width = int(thumbnail_width)
    # Recompute image width, because actual width of the preview thumbnails may be a few pixels less due to scaling and rounding to integer pixels
    image_width = thumbnail_width * columns + x_spacing * (columns + 1)
    image_height = header_height + thumbnail_height * rows + y_spacing * (rows + 1)

    if verbose:
        print('Image dimensions: {} x {} -> {} x {} thumbnails with dimensions {} x {}'.format(image_width, image_height, columns, rows, thumbnail_width, thumbnail_height))

    # PIL image for the preview thumbnails
    thumbnails_image = Image.new('RGB', (image_width, image_height), color=PIL_COLOR_WHITE)
    # PIL draw for adding text to the image
    thumbnails_draw = ImageDraw.Draw(thumbnails_image)

    # Drawing the header text
    x = x_spacing
    y = y_spacing
    thumbnails_draw.text((x, y), file_info, PIL_COLOR_BLACK, font=header_font)
    y += text_height_file_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), size_info, PIL_COLOR_BLACK, font=header_font)
    y += text_height_size_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), video_info, PIL_COLOR_BLACK, font=header_font)
    y += text_height_video_info
    y += text_line_spacing
    thumbnails_draw.text((x, y), audio_info, PIL_COLOR_BLACK, font=header_font)

    # Video time at which to capture the next preview
    time = skip_seconds
    thumbnail_count = 0
    for row_index in range(rows):
        y = header_height + row_index * thumbnail_height + (row_index + 1) * y_spacing
        for column_index in range(columns):
            x = column_index * thumbnail_width + (column_index + 1) * x_spacing
            frame = video_clip.get_frame(time)
            image = Image.fromarray(frame)
            image.thumbnail((thumbnail_width, thumbnail_height))
            thumbnails_image.paste(image, box=(x, y))
            thumbnail_count += 1
            if verbose:
                print('Captured preview thumbnail #{} of frame at {:.3f} s'.format(thumbnail_count, time))
            time += time_step

    # Save the preview thumbnails image
    image_path = '{}.jpg'.format(file_path)
    if verbose:
        print('Saving preview thumbnails image to \'{}\''.format(image_path))
    thumbnails_image.save(image_path, quality=jpeg_quality)

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

def process_file_or_directory(path: str, recursive: bool, width: int, columns: int, rows: int, spacing: int,
                              skip_seconds: float, jpeg_quality: int, verbose: bool) -> None:
    """
    Process a file or directory and create preview thumbnails of identified video files.

    If called on a file, preview thumbnails are created if the file is a video.
    If called on a directory, preview thumbnails are created of video files found in the directory.

    Parameters:
    path (str): The absolute or relative path of the file or directory.
    recursive (bool): If path is a directory and True, process any subdirectories as well.
    width (int): The width in pixels of the created preview thumbnails image.
    columns (int): The number of thumbnail columns.
    rows (int): The number of thumbnail rows.
    spacing (int): The spacing in pixels between and around the preview thumbnails.
    skip_seconds (float): The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail.
    jpeg_quality (int): The quality of the JPEG image files that are created.
    verbose (bool): Print verbose information and messages.
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
                create_preview_thumbnails(file_path, width, columns, rows, spacing, skip_seconds, jpeg_quality, verbose)
            except Exception as e:
                print('An error occurred:\n{}\nSkipping file \'{}\'.'.format(e, os.path.abspath(file_path)), file=sys.stderr)

def parse_args() -> Namespace:
    parser = ArgumentParser(description='Pyhton Video Thumbnailer. Command line tool for creating video preview thumbnails.',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--width',
                         nargs=1,
                         type=int,
                         default=DEFAULT_WIDTH,
                         help='The intended width of the preview thumbnails image in px. Actual width may be slightly less due rounding upon scaling.')
    parser.add_argument('--columns',
                         nargs=1,
                         type=int,
                         default=DEFAULT_COLUMNS,
                         help='The number of preview thumbnail columns.')
    parser.add_argument('--rows',
                         nargs=1,
                         type=int,
                         default=DEFAULT_ROWS,
                         help='The number of preview thumbnail rows.')
    parser.add_argument('--spacing',
                         nargs=1,
                         type=int,
                         default=DEFAULT_SPACING,
                         help='The spacing between and around the preview thumbnails in px.')
    parser.add_argument('--skip-seconds',
                         nargs=1,
                         type=float,
                         default=DEFAULT_SKIP_SECONDS,
                         help='The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail.')
    parser.add_argument('--jpeg-quality',
                         nargs=1,
                         type=int,
                         default=DEFAULT_JPEG_QUALITY,
                         help='The quality of the JPEG image files that are created.')
    parser.add_argument('--recursive',
                         action='store_true',
                         help='If creating preview thumbnails of video files in a directory, process subdirectories recursively.')
    parser.add_argument('--verbose',
                         action='store_true',
                         help='Print verbose information and messages.')
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
    process_file_or_directory(args.filename, args.recursive, args.width, args.columns, args.rows, args.spacing,
                              args.skip_seconds, args.jpeg_quality, args.verbose)
