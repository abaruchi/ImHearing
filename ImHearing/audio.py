""" Routines to record audio from environment and store the files
"""

import wave
from datetime import datetime
from os import path, stat
from uuid import uuid4

from pony.orm import db_session
from pyaudio import PyAudio, paInt16

from ImHearing import logger

# Default Values to be used for recording
CHUNK = 512
DEVICE_INDEX = 2
FORM_1 = paInt16
CHANNELS = 1
SAMPLE_RATE = 44100


@db_session
def start_recording(db, global_config):
    """
    Main routine to perform environment records.
    :param db: DB Connection to Pony
    :param global_config: Global Configuration dict
    :return: Record Object or -1 on error
    """

    if not path.isdir(global_config['record_path']):
        return -1
    
    audio = PyAudio()
    frames = list()
    stream = audio.open(format=FORM_1,
                        rate=SAMPLE_RATE,
                        channels=CHANNELS,
                        input_device_index=DEVICE_INDEX,
                        input=True, frames_per_buffer=CHUNK)
    record_uuid = uuid4()
    record_file = get_filename(
        file_name_parts=[str(record_uuid)[35 - 11:],
                         str(int(datetime.now().timestamp()))])

    # Start the Recording
    time_start = datetime.now()
    for _ in range(0, (SAMPLE_RATE // CHUNK) * int(global_config['record_period'])):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    time_end = datetime.now()
    # Finish the Recording

    input_file = global_config['record_path'] + record_file
    wavefile = wave.open(input_file, 'wb')
    wavefile.setnchannels(CHANNELS)
    wavefile.setsampwidth(audio.get_sample_size(FORM_1))
    wavefile.setframerate(SAMPLE_RATE)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    record_new = db.Record(
        start=time_start,
        end=time_end,
        size=stat(input_file).st_size / (1024 * 1024),
        path=input_file,
        status='recorded'
    )

    return record_new


def get_filename(file_name_parts=None):
    """
    This routine creates the filename to be used to store the record.
    :param file_name_parts: file name parts
    :return: File Name to store the record
    """
    file_partial = ''
    if file_name_parts is not None:
        for part in file_name_parts:
            file_partial = file_partial + '_' + part
    output_file = 'record_' + file_partial + '.wav'
    return output_file
