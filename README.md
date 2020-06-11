# pyvideothumbnailer
**Pyhton Video Thumbnailer** is a command line tool for creating video preview thumbnails. It can be used to create preview images of individual video files, videos located in a directory and optionally its subdirectories. It is based on MoviePy, MediaInfo and PIL.

## Prerequisites

Install the dependencies MoviePy, MediaInfo and PIL (Pillow), e.g. using the Python Package Installer

```
pip3 install moviepy pymediainfo Pillow
```

## Options

Python Video Thumbnailer currently has the following options

```
usage: pyvideothumbnailer.py [-h] [--width WIDTH] [--columns COLUMNS] [--rows ROWS] [--spacing SPACING] [--header-font HEADER_FONT]
                             [--header-font-size HEADER_FONT_SIZE] [--timestamp-font TIMESTAMP_FONT] [--timestamp-font-size TIMESTAMP_FONT_SIZE]
                             [--skip-seconds SKIP_SECONDS] [--suffix SUFFIX] [--jpeg-quality JPEG_QUALITY] [--override-existing] [--recursive]
                             [--output-directory OUTPUT_DIRECTORY] [--raise-errors] [--verbose]
                             [filename]

Pyhton Video Thumbnailer. Command line tool for creating video preview thumbnails.

positional arguments:
  filename              Video file of which to create preview thumbnails or directory, where multiple video files are located. File name in the current working
                        directory or path. If the argument is omitted, preview thumbnails are generated for video files in the current working directory. (default:
                        <CURRENT WORKING DIRECTORY>)

optional arguments:
  -h, --help            show this help message and exit
  --width WIDTH         The intended width of the preview thumbnails image in px. Actual width may be slightly less due rounding upon scaling. (default: 800)
  --columns COLUMNS     The number of preview thumbnail columns. (default: 4)
  --rows ROWS           The number of preview thumbnail rows. (default: 3)
  --spacing SPACING     The spacing between and around the preview thumbnails in px. (default: 2)
  --header-font HEADER_FONT
                        The name of a true type font to use for the header text providing information on the video file and its metadata. If omitted, a built-in
                        default font is used. (default: None)
  --header-font-size HEADER_FONT_SIZE
                        The font size of the header font, if a true type font is specified. With the built-in font, this value is ignored. (default: 14)
  --timestamp-font TIMESTAMP_FONT
                        The name of a true type font to use for the preview thumbnail timestamps. If omitted, a built-in default font is used. (default: None)
  --timestamp-font-size TIMESTAMP_FONT_SIZE
                        The font size of the timestamp font, if a true type font is specified. With the built-in font, this value is ignored. (default: 12)
  --skip-seconds SKIP_SECONDS
                        The number of seconds to skip at the beginning of the video before capturing the first preview thumbnail. (default: 10.0)
  --suffix SUFFIX       An optional suffix to append to the file name of the generated preview thumbnails images. (default: None)
  --jpeg-quality JPEG_QUALITY
                        The quality of the JPEG image files that are created. (default: 95)
  --override-existing   Override any existing image files, which have the same name as the generated images. By default, a preview thumbnails image is not created,
                        if the file to be created already exists. (default: False)
  --recursive           If creating preview thumbnails of video files in a directory, process subdirectories recursively. (default: False)
  --output-directory OUTPUT_DIRECTORY
                        A directory, where all created preview thumbnails images should be saved. If omitted, preview thumbnails images are saved in the same
                        directory, where the respective video file is located. (default: None)
  --raise-errors        Stop if an error occurs by raising it. By default, errors are ignored and the affected preview thumbnails image is skipped. This is useful,
                        when processing multiple video files in a directory. (default: False)
  --verbose             Print verbose information and messages. (default: False)
```

## Links

[MoviePy](https://github.com/Zulko/moviepy)

[MediaInfo](https://github.com/sbraz/pymediainfo)

[Pillow](https://python-pillow.org/)
