# exif-reader

Reads EXIF infos from a bunch of images do things with it.

## build-metadata-file.py
Takes all images from current folder and gathers their EXIF infos into a small `exif-catalog.db` database file in that folder, so that they can:
- Be renamed
- Be searched
- Reveal shooting informations that can be hard to get

## prefix-files-with-exif-date.py
Rename all images with their shooting date as a prefix.\
Use `build-metadata-file.py` before.
