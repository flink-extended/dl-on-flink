from flink_ml_workflow.proto.meta_data_pb2 import *
from flink_ml_workflow.vertex.base_vertex import BaseVertex
from enum import Enum


class ModelType(str, Enum):
    CHECKPOINT = 'CHECKPOINT'
    SAVED_MODEL = 'SAVED_MODEL'
    H5 = 'H5'


class ModelVersion(BaseVertex):
    def __init__(self,
                 version,
                 model_uri: str,
                 log_uri: str,
                 properties=None):
        super(ModelVersion, self).__init__(version, properties)
        self.version = version
        self.model_uri = model_uri
        self.log_uri = log_uri

    def to_proto(self):
        model_version_proto = ModelVersionProto()
        return self.set_proto(model_version_proto)

    def set_proto(self, model_version_proto):
        model_version_proto.meta.name = self.name
        model_version_proto.modelUri = self.model_uri
        model_version_proto.logUri = self.log_uri
        model_version_proto.version = self.version
        return model_version_proto


class Model(BaseVertex):

    def __init__(self,
                 name,
                 model_type: ModelType,
                 uri: str,
                 version_list: list = None,
                 properties=None):
        super(Model, self).__init__(name, properties)
        self.model_type = model_type
        self.uri = uri
        if version_list is None:
            self.version_list = list()
        else:
            self.version_list = version_list

    def add_version(self, version: ModelVersion):
        self.version_list.append(version)
        return self

    def to_proto(self):
        model_proto = ModelProto()
        return self.set_proto(model_proto)

    def set_proto(self, model_proto):
        model_proto.meta.name = self.name
        for i in self.properties:
            model_proto.meta.properties[i] = self.properties[i]
        if ModelType.CHECKPOINT == self.model_type:
            model_proto.modelType = ModelTypeProto.CHECKPOINT
        elif ModelType.SAVED_MODEL == self.model_type:
            model_proto.modelType = ModelTypeProto.SAVED_MODEL
        else:
            model_proto.modelType = ModelTypeProto.H5
        for i in self.version_list:
            model_proto.versionList.append(i.to_proto())
        return model_proto


if __name__ == "__main__":
    version1 = ModelVersion(version='v1',
                            model_uri='aa/v1',
                            log_uri='aa/l1')
    version2 = ModelVersion(version='v2',
                            model_uri='aa/v2',
                            log_uri='aa/l2')
    model = Model(name="model",
                  model_type=ModelType.SAVED_MODEL,
                  uri="aa")
    model.add_version(version1)
    model.add_version(version2)

    print(model.to_json())
