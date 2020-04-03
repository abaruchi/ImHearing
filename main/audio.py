"""
Classes to Record, Compress, Store and Upload the Audios recorded.
"""

import time
import wave
from datetime import datetime
from os import getcwd, stat

import pyaudio


class Recorder(object):
    form_1 = pyaudio.paInt16
    channels = 1
    sample_rate = 44100

    def __init__(self, timestamp=None):
        # Values that can be changed
        self.record_time = 600
        self.chunk = 512
        self.device_index = 2
        self.timestamp = int(time.time()) if timestamp is None else timestamp
        self.records_file_dict = dict()

    def record_start(self):
        """
        Start the audio recording.
        :return: Returns the file path with the recorded data.
        """
        audio = pyaudio.PyAudio()
        frames = []
        stream = audio.open(format=Recorder.form_1,
                            rate=Recorder.sample_rate,
                            channels=Recorder.channels,
                            input_device_index=self.device_index,
                            input=True, frames_per_buffer=self.chunk)

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

        input_file = self.__file_output()
        wavefile = wave.open(input_file, 'wb')
        wavefile.setnchannels(Recorder.channels)
        wavefile.setsampwidth(audio.get_sample_size(Recorder.form_1))
        wavefile.setframerate(Recorder.sample_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        self.records_file_dict[str(datetime.now())] = {
            'time_start': time_start,
            'time_end': time_end,
            'file_path': input_file,
            'uploaded': False,
            'file_size': stat(input_file).st_size/(1024*1024)
        }

        return input_file

    def __file_output(self, base_path=None):
        output_file = 'record_' + str(self.timestamp) + '.wav'
        output_path = getcwd() if base_path is None else base_path
        return output_path + '/' + output_file

    def recorded_files(self):
        return self.records_file_dict

    #-- Setters and Getters --#
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


class Compressor(object):
    pass


class Uploader(object):
    pass
