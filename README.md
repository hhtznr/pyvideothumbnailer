# pyvideothumbnailer
**Pyhton Video Thumbnailer** is a command line tool for creating video preview thumbnails. It can be used to create preview images of individual video files, videos located in a directory and optionally its subdirectories. It is based on [PyAV](https://github.com/PyAV-Org/PyAV), [MediaInfo](https://github.com/sbraz/pymediainfo) and PIL/[Pillow](https://python-pillow.org/).

## Installation

Pyhton Video Thumbnailer has the following dependencies:

  * [Python 3](https://www.python.org/downloads/) (3.7 or newer)
  * [PyAV](https://github.com/PyAV-Org/PyAV)
  * [MediaInfo](https://github.com/sbraz/pymediainfo)
  * PIL/[Pillow](https://python-pillow.org/)

The python packages can be installed using the _Python Package Installer_:

```
pip3 install av pymediainfo Pillow
```

All code of Python Video Thumbnailer is contained in the file [pyvideothumbnailer](https://github.com/hhtznr/pyvideothumbnailer/blob/master/pyvideothumbnailer). It can be placed in `/usr/local/bin` or another directory on the system PATH variable and be made executable. Alternatively, it can be invoked by supplying its path as argument to the Python interpreter `python3`.

The optional configuration file [.pyvideothumbnailer.conf](https://github.com/hhtznr/pyvideothumbnailer/blob/master/.pyvideothumbnailer.conf) needs to be placed in the user's home directory.

As of [Ubuntu](https://ubuntu.com/) 22.04 LTS (Jammy Jellyfish), Ubuntu users can alternatively install the DEB package provided in the [release section](https://github.com/hhtznr/pyvideothumbnailer/releases) or install from this [Ubuntu PPA](https://launchpad.net/~haraldhetzner/+archive/ubuntu/ppa).

## Usage

Python Video Thumbnailer has meaningful defaults. So you can just start creating your first preview thumbnails image of an individual video file by invoking:

```
pyvideothumbnailer [VIDEO FILE]
```

or to create thumbnails of all video files located in the current working directory:

```
pyvideothumbnailer
```

or to create thumbnails of all video files located in a directory:

```
pyvideothumbnailer [DIRECTORY CONTAINING VIDEOS]
```

or in case that you want to create previews of videos in subdirectories as well:

```
pyvideothumbnailer --recursive [DIRECTORY CONTAINING VIDEOS]
```

## Examples

Here are two examples how it works creating preview thumbmnails of [Big Buck Bunny](https://peach.blender.org/).

Using defaults:

```
pyvideothumbnailer bbb_sunflower_1080p_60fps_normal.mp4
```

![bbb_sunflower_1080p_60fps_normal_defaults mp4](https://user-images.githubusercontent.com/57875126/160253963-46528e85-ae1f-4518-a255-4e57ff7011ca.jpg)

White header font on black background, [DejaVuSans TrueType font](https://dejavu-fonts.github.io/) instead of the built-in font, adding a comment at the bottom of the header, custom preview thumbnails image width and 5 x 4 preview thumbnails:

```
pyvideothumbnailer --background-color black --header-font-color white --header-font DejaVuSans.ttf --timestamp-font DejaVuSans.ttf --comment-text "Created with pyvideothumbnailer" --width 1024 --columns 5 --rows 4 bbb_sunflower_1080p_60fps_normal.mp4
```

![bbb_sunflower_1080p_60fps_normal mp4_example5](https://user-images.githubusercontent.com/57875126/160254972-246c865e-8065-4a66-b947-81942af2a879.jpg)

## Documentation

Visit the [wiki page](https://github.com/hhtznr/pyvideothumbnailer/wiki) for more comprehensive information on installation and usage.
