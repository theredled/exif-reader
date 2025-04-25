import sqlite3
import os
import mimetypes
import json
import traceback
#from exif import Image
#import exiftool
import subprocess
import re
import shlex
import sys

def rebuild_db(db_filename, dir_path):
    open(db_filename, 'w').close()
    con = sqlite3.connect(db_filename)
    cur = con.cursor()
    cur.execute("CREATE TABLE file(original_filename, mimetype, has_exif, type, original_datetime, filesize, gps_latitude, gps_longitude, gps_altitude, exif_data)")
    files = os.listdir(dir_path)
    print("Found %d files, waiting for exiftool..." % len(files))

    output = subprocess.check_output('exiftool -progress -j -c "%.10f" -d "%Y-%m-%d %H:%M:%S" -DateTimeOriginal -GpsLatitude '
                                     '-GpsLongitude -GpsAltitude -MimeType -CreateDate -CreationDate .', shell=True)
    all_files_metadata = json.loads(output)

    print("\n")

    for i, metadata in enumerate(all_files_metadata):
        print("Processing file %i/%i..." % (i + 1, len(files)), end="\r")
        file_path = metadata['SourceFile']

        mimetype = mimetypes.guess_type(file_path)[0]
        if not (mimetype.startswith('image/') or mimetype.startswith('video/')):
            return False

        original_filename = os.path.basename(file_path)
        if re.search('^\d{8}-', original_filename):
            original_filename = re.sub('^\d{8}-', '', original_filename)

        if 'DateTimeOriginal' in metadata:
            original_datetime = metadata['DateTimeOriginal']
        elif 'CreateDate' in metadata:
            original_datetime = metadata['CreateDate']
        elif 'CreationDate' in metadata:
            original_datetime = metadata['CreationDate']
        else:
            original_datetime = None
            print("\nNo original datetime found for file %s" % original_filename)

        if original_datetime == '0000:00:00 00:00:00':
            original_datetime = None
            print("\nNo original datetime found for file %s" % original_filename)

        data = {
            'has_exif': metadata is not None,
            'type': 'video' if mimetype.startswith('video/') else 'image',
            'filesize': os.path.getsize(file_path),
            'mimetype': metadata['MIMEType'] if 'MIMEType' in metadata else mimetype,
            'original_datetime': original_datetime,
            'gps_latitude': metadata['GPSLatitude'] if 'GPSLatitude' in metadata else None,
            'gps_longitude': metadata['GPSLongitude'] if 'GPSLongitude' in metadata else None,
            'gps_altitude': metadata['GPSAltitude'] if 'GPSAltitude' in metadata else None,
            'exif_data': metadata  # image.get_all()
        }

        ret = cur.execute(
            "INSERT INTO file(original_filename, mimetype, has_exif, type, original_datetime, filesize, gps_latitude, gps_longitude, gps_altitude, exif_data) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                original_filename,
                data['mimetype'],
                data['has_exif'],
                data['type'],
                data['original_datetime'],
                data['filesize'],
                data['gps_latitude'],
                data['gps_longitude'],
                data['gps_altitude'],
                json.dumps(data['exif_data'])
            ))
        con.commit()

    print("\n")
    print("Done")


# Driver Code
if __name__ == "__main__":
    rebuild_db("exif-catalog.db", os.getcwd())
