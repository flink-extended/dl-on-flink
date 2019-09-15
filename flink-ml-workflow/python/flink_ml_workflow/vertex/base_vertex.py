from abc import ABCMeta, abstractmethod
from google.protobuf import json_format


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

    def from_json(self):
        pass

    @abstractmethod
    def to_proto(self):
        pass
