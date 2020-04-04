"""
Implements routines and classes used to Audio Files Post-Processing
"""

from datetime import datetime
import zipfile
from os import getcwd, makedirs, path
from uuid import uuid4


def audio_processor(metadata_dict, base_path=None):
    """
    Creates the Archives with audio files.

    :param metadata_dict: dict with audio metadata
    :param base_path: basedir used to create the archive directory (YYYYMMDD)
    :return: the updated metadata dict
    """
    if len(metadata_dict) == 0:
        raise ValueError

    # Check and Prepare the Directory to store the Archive
    archive_dir = datetime.now().strftime("%Y%m%d")
    archive_base_dir = getcwd() if base_path is None else base_path

    if not path.isdir(archive_base_dir):
        makedirs(archive_base_dir)

    archive_full_basedir = archive_base_dir + '/' + archive_dir
    if not path.isdir(archive_full_basedir):
        makedirs(archive_full_basedir)

    # Create a zip_archive with all files
    zip_file_name = archive_full_basedir + '/' + str(uuid4()) + '_' + \
                    str(int(datetime.now().timestamp())) + '.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zip_archive:
        for element in metadata_dict.keys():
            zip_archive.write(metadata_dict[element]['file_path'])
            metadata_dict[element]['compressed'] = True
            metadata_dict[element]['zip_archive'] = zip_file_name

    return metadata_dict

