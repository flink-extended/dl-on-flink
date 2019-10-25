from flink_ml_workflow.store.abstract_store import AbstractStore
from flink_ml_workflow.vertex.example import Example
from flink_ml_workflow.vertex.history import History
from flink_ml_workflow.vertex.model import ModelVersion, Model
from flink_ml_workflow.vertex.project import Project


class LocalStore(AbstractStore):
    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir

    def get_model_by_id(self, model_id):
        pass

    def get_model_by_name(self, name):
        pass

    def list_model(self, page_size, offset):
        pass

    def list_model_version(self, model_id, page_size, offset):
        pass

    def get_model_version_by_id(self, version_id):
        pass

    def get_model_version_by_name(self, version_name):
        pass

    def save_model(self, model: Model):
        pass

    def save_model_version(self, model_version: ModelVersion):
        pass

    def save_model_versions(self, version_list: list):
        pass

    def get_example_by_id(self, experiment_id):
        pass

    def get_example_by_name(self, experiment_name):
        pass

    def list_example(self, page_size, offset):
        pass

    def save_example(self, example: Example):
        pass

    def get_project_by_id(self, project_id):
        pass

    def get_project_by_name(self, project_name):
        pass

    def save_project(self, project: Project):
        pass

    def list_projects(self, page_size, offset):
        pass

    def get_history_by_id(self, history_id):
        pass

    def get_history_by_name(self, history_name):
        pass

    def save_history(self, history: History):
        pass

    def list_history(self, page_size, offset):
        pass
