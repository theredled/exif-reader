import datetime
import glob
import sqlite3
import os
import mimetypes
import json
import traceback
#from exif import Image
#import exiftool
import subprocess
import shlex
import sys

sql_date_format = '%Y-%m-%d %H:%M:%S'


def rename_files(db_filename, dir_path):
    os.chdir(dir_path)
    con = sqlite3.connect(db_filename)
    cur = con.cursor()
    req = cur.execute("SELECT original_filename, original_datetime FROM file")
    files = req.fetchall()

    for i, file in enumerate(files):
        original_datetime = file[1]
        original_filename = file[0]

        # -- Find file
        filename = original_filename
        if not os.path.isfile(filename):
            found_list = glob.glob('????????-' + filename)
            if len(found_list) > 1:
                print('Several %s not found, skipping' % original_filename)
                continue
            if len(found_list) > 0:
                filename = found_list[0]
            else:
                print('%s or prefixed not found, skipping' % original_filename)
                continue

        # -- With no date
        if not original_datetime:
            print('No original datetime for %s, removing prefix if existing' % original_filename)
            new_filename = original_filename
        # -- With date
        else:
            dt = datetime.datetime.strptime(original_datetime, sql_date_format)
            new_filename = dt.strftime('%Y%m%d') + '-' + original_filename

        print("Processing file %i/%i (%s > %s)..." % (i + 1, len(files), original_filename, new_filename))

        os.rename(filename, new_filename)
    print('Done')


# Driver Code
if __name__ == "__main__":
    input = input('Vous allez renommer toutes les images recensées du dossier courant, OK ? Y/N')
    if (input.upper() == 'Y'):
        rename_files("exif-catalog.db", os.getcwd())
    else:
        print('Annulé.')
