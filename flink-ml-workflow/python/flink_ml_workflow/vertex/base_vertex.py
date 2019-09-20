from abc import ABCMeta, abstractmethod
from google.protobuf import json_format
from enum import Enum


class RunMode(str, Enum):
    STREAM = 'STREAM'
    BATCH = 'BATCH'


class BaseVertex(object):

    def __init__(self,
                 name,
                 properties=None):
        if properties is None:
            properties = {}
        self.name = name
        self.properties = properties

    def to_json(self):
        proto = self.to_proto()
        json_string = json_format.MessageToJson(proto)
        return json_string

    def from_json(self, json_str):
        pass

    @abstractmethod
    def to_proto(self):
        pass

    @abstractmethod
    def set_proto(self, proto):
        pass
