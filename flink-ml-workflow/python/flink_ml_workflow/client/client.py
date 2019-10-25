from flink_ml_workflow.artifact.artifact_repo import ArtifactRepository
from flink_ml_workflow.store.abstract_store import AbstractStore
from flink_ml_workflow.vertex.model import Model, ModelVersion
from flink_ml_workflow.vertex.example import Example
from flink_ml_workflow.vertex.history import History
from flink_ml_workflow.vertex.project import Project


class Client(object):
    def __init__(self, store: AbstractStore, artifact_repo: ArtifactRepository) -> None:
        super().__init__()
        self.store = store
        self.artifact_repo = artifact_repo

    # artifact repo api

    def log_artifact(self, local_file, artifact_path=None):
        return self.artifact_repo.log_artifact(local_file, artifact_path)

    def log_artifacts(self, local_dir, artifact_path=None):
        return self.artifact_repo.log_artifacts(local_dir, artifact_path)

    def list_artifacts(self, path):
        return self.artifact_repo.list_artifacts(path)

    def download_artifacts(self, artifact_path, dst_path=None):
        return self.artifact_repo.download_artifacts(artifact_path, dst_path)

    # store api

    def get_model_by_id(self, model_id):
        return self.store.get_model_by_id(model_id)

    def get_model_by_name(self, name):
        return self.store.get_model_by_name(name)

    def list_model(self, page_size, offset):
        return self.store.list_model(page_size, offset)

    def list_model_version(self, model_id, page_size, offset):
        return self.store.list_model_version(model_id, page_size, offset)

    def get_model_version_by_id(self, version_id):
        return self.store.get_model_version_by_id(version_id)

    def get_model_version_by_name(self, version_name):
        return self.store.get_model_version_by_name(version_name)

    def save_model(self, model: Model):
        return self.store.save_model(model)

    def save_model_version(self, model_version: ModelVersion):
        return self.store.save_model_version(model_version)

    def save_model_versions(self, version_list: list):
        return self.store.save_model_versions(version_list)

    '''
        example api
    '''

    def get_example_by_id(self, experiment_id):
        return self.store.get_example_by_id(experiment_id)

    def get_example_by_name(self, experiment_name):
        return self.store.get_example_by_name(experiment_name)

    def list_example(self, page_size, offset):
        return self.store.list_example(page_size, offset)

    def save_example(self, example: Example):
        return self.store.save_example(example)

    '''
        project api
    '''

    def get_project_by_id(self, project_id):
        return self.store.get_project_by_id(project_id)

    def get_project_by_name(self, project_name):
        return self.store.get_project_by_name(project_name)

    def save_project(self, project: Project):
        return self.store.save_project(project)

    def list_projects(self, page_size, offset):
        return self.store.list_projects(page_size, offset)

    '''
        history api
    '''

    def get_history_by_id(self, history_id):
        return self.store.get_history_by_id(history_id)

    def get_history_by_name(self, history_name):
        return self.store.get_history_by_name(history_name)

    def save_history(self, history: History):
        return self.store.save_history(history)

    def list_history(self, page_size, offset):
        return self.store.list_history(page_size, offset)

