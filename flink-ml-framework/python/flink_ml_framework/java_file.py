import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import java_file_c
import struct
import json


class JavaFile(object):
    def __init__(self, read_file, write_file):
        self.read_file = read_file
        self.write_file = write_file
        self.java_file_c = java_file_c.JavaFile(read_file, write_file)

    def read(self, data_len):
        data = self.java_file_c.readBytes(data_len)
        if 0 == len(data):
            raise EOFError("file reach end!")
        return data

    def write(self, data, data_len):
        return self.java_file_c.writeBytes(data, data_len)


class BytesRecorder(object):
    def __init__(self, read_file, write_file):
        self.java_file = JavaFile(read_file, write_file)

    def read_record(self):
        res = self.java_file.read(4)
        data_len, = struct.unpack("<i", res)
        return self.java_file.read(data_len)

    def write_record(self, data):
        data_len = len(data)
        json_len = struct.pack("<i", data_len)
        res = self.java_file.write(json_len, 4)
        if res is False:
            return False
        res = self.java_file.write(data, data_len)
        return res


class JsonRecorder(object):
    def __init__(self, read_file, write_file):
        self.java_file = JavaFile(read_file, write_file)

    def read_record(self):
        res = self.java_file.read(4)
        data_len, = struct.unpack("<i", res)
        data = self.java_file.read(data_len)
        return json.loads(data)

    def write_record(self, data):
        json_data = json.dumps(data)
        data_len = len(json_data)
        json_len = struct.pack("<i", data_len)
        res = self.java_file.write(json_len, 4)
        if res is False:
            return False
        res = self.java_file.write(json_data, data_len)
        return res
