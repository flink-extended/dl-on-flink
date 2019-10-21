from abc import abstractmethod, ABCMeta
from flink_ml_workflow.vertex.model import Model, ModelVersion
from flink_ml_workflow.vertex.example import Example
from flink_ml_workflow.vertex.transformer import Transformer
from flink_ml_workflow.vertex.trainer import Trainer
from flink_ml_workflow.vertex.workflow import WorkFlow
from flink_ml_workflow.vertex.history import History


class AbstractStore:
    """
    Abstract class for Backend Storage.
    This class defines the API interface for front ends to connect with various types of backends.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Empty constructor for now. This is deliberately not marked as abstract, else every
        derived class would be forced to create one.
        """
        pass

    '''
        model api
    '''
    @abstractmethod
    def get_model_by_id(self, model_id):
        pass

    @abstractmethod
    def get_model_by_name(self, name):
        pass

    @abstractmethod
    def list_model(self, page_size, offset):
        pass

    @abstractmethod
    def list_model_version(self, model_id, page_size, offset):
        pass

    @abstractmethod
    def get_model_version_by_id(self, version_id):
        pass

    @abstractmethod
    def get_model_version_by_name(self, version_name):
        pass

    @abstractmethod
    def save_model(self, model: Model):
        pass

    @abstractmethod
    def save_model_version(self, model_version: ModelVersion):
        pass

    @abstractmethod
    def save_model_versions(self, version_list: list):
        pass

    '''
        example api
    '''

    @abstractmethod
    def get_example_by_id(self, experiment_id):
        pass

    @abstractmethod
    def get_example_by_name(self, experiment_name):
        pass

    @abstractmethod
    def list_example(self, page_size, offset):
        pass

    @abstractmethod
    def save_example(self, example: Example):
        pass

    '''
        transformer api
    '''

    @abstractmethod
    def get_transformer_by_id(self, transformer_id):
        pass

    @abstractmethod
    def get_transformer_by_name(self, transformer_name):
        pass

    @abstractmethod
    def save_transformer(self, transformer: Transformer):
        pass

    @abstractmethod
    def list_transformer(self, transformer_id, page_size, offset):
        pass

    '''
        trainer api
    '''
    @abstractmethod
    def get_trainer_by_id(self, trainer_id):
        pass

    @abstractmethod
    def get_trainer_by_name(self, trainer_name):
        pass

    @abstractmethod
    def save_trainer(self, trainer: Trainer):
        pass

    @abstractmethod
    def list_trainer(self, page_size, offset):
        pass

    '''
        execution api
    '''

    @abstractmethod
    def get_execution_by_id(self, execution_id):
        pass

    @abstractmethod
    def get_execution_by_name(self, experiment_name):
        pass

    @abstractmethod
    def save_execution(self, execution):
        pass

    @abstractmethod
    def list_execution(self, page_size, offset):
        pass

    '''
        workflow api
    '''

    @abstractmethod
    def get_workflow_by_id(self, workflow_id):
        pass

    @abstractmethod
    def get_workflow_by_name(self, workflow_name):
        pass

    @abstractmethod
    def save_work_flow(self, workflow:WorkFlow):
        pass

    @abstractmethod
    def list_workflow(self, page_size, offset):
        pass

    '''
        history api
    '''

    @abstractmethod
    def get_history_by_id(self, history_id):
        pass

    @abstractmethod
    def get_history_by_name(self, history_name):
        pass

    @abstractmethod
    def save_history(self, history: History):
        pass

    @abstractmethod
    def list_history(self, page_size, offset):
        pass
