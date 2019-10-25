from enum import Enum
from flink_ml_workflow.proto.meta_data_pb2 import *
from flink_ml_workflow.vertex.base_vertex import BaseVertex


class ProjectType(str, Enum):
    GIT = "GIT"
    PACKAGE = "PACKAGE"
    LOCAL_DIR = "LOCAL_DIR"


class Project(BaseVertex):
    def __init__(self,
                 name,
                 project_type: ProjectType,
                 uri: str,
                 user: str,
                 password: str,
                 properties: dict = None):
        super(Project, self).__init__(name, properties)
        self.project_type = project_type
        self.uri = uri
        self.user = user
        self.password = password

    def to_proto(self):
        project_proto = ProjectProto()
        return self.set_proto(project_proto)

    def set_proto(self, project_proto):
        project_proto.meta.name = self.name
        for i in self.properties:
            project_proto.meta.properties[i] = self.properties[i]

        if self.project_type == ProjectType.GIT:
            project_proto.projectType = ProjectType.GIT
        else:
            project_proto.projectType = ProjectType.PACKAGE

        project_proto.user = self.user
        project_proto.password = self.password
        project_proto.uri = self.uri
        return project_proto


if __name__ == "__main__":
    project = Project(name="project",
                      project_type=ProjectType.GIT,
                      user="user",
                      password="password",
                      uri="./log")

    print(project.to_json())
