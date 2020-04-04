"""
Classes to Record, Compress, Store and Upload the Audios recorded.
"""

import wave
from datetime import datetime
from os import getcwd, stat
from uuid import uuid4

import pyaudio


class Recorder(object):
    form_1 = pyaudio.paInt16
    channels = 1
    sample_rate = 44100

    def __init__(self):
        # Values that can be changed
        self.record_time = 600
        self.chunk = 512
        self.device_index = 2
        self.records_file_dict = dict()

    def record_start(self):
        """
        Start the audio recording.
        :return: Returns the file path with the recorded data.
        """
        audio = pyaudio.PyAudio()
        frames = list()
        stream = audio.open(format=Recorder.form_1,
                            rate=Recorder.sample_rate,
                            channels=Recorder.channels,
                            input_device_index=self.device_index,
                            input=True, frames_per_buffer=self.chunk)
        record_uuid = uuid4()
        record_file = self.__file_output(
            file_name_parts=[str(record_uuid)[35 - 11:],
                             str(int(datetime.now().timestamp()))])
        # Start the Recording
        time_start = datetime.now()
        for _ in range(0, (self.sample_rate // self.chunk) * self.record_time):
            data = stream.read(self.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()
        time_end = datetime.now()
        # Finish the Recording

        input_file = record_file
        wavefile = wave.open(input_file, 'wb')
        wavefile.setnchannels(Recorder.channels)
        wavefile.setsampwidth(audio.get_sample_size(Recorder.form_1))
        wavefile.setframerate(Recorder.sample_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        self.records_file_dict[str(record_uuid)] = {
            'time_start': time_start,
            'time_end': time_end,
            'file_path': record_file,
            'zip_archive': None,
            'registered': False,
            'compressed': False,
            'uploaded': False,
            'file_size': stat(record_file).st_size / (1024 * 1024)
        }

        return input_file

    def __file_output(self, base_path=None, file_name_parts=None):
        file_partial = ''
        if file_name_parts is not None:
            for part in file_name_parts:
                file_partial = file_partial + '_' + part
        output_file = 'record_' + file_partial + '.wav'
        output_path = getcwd() if base_path is None else base_path
        return output_path + '/' + output_file

    def get_metadata_dict(self):
        return self.records_file_dict

    # -- Setters and Getters --#
    @property
    def record_time(self):
        return self.__record_time

    @record_time.setter
    def record_time(self, value):
        self.__record_time = value

    @property
    def chunk(self):
        return self.__chunk

    @chunk.setter
    def chunk(self, value):
        self.__chunk = value

    @property
    def device_index(self):
        return self.__device_index

    @device_index.setter
    def device_index(self, value):
        self.__device_index = value
