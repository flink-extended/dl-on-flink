import yaml
import os
from flink_ml_workflow.exception.workflow_exception import WorkflowException


ML_PROJECT_FILE_NAME = "MLProject.yaml"
PYTHON_INTERPRETER = "python_interpreter"
PIP = "pip"
VIRTUAL_ENV = "virtual_env"
PIP_DEPENDENCIES = "pip_dependencies"
DEPENDENCIES = "dependencies"


def load_project(directory):
    ml_project_path = os.path.join(directory, ML_PROJECT_FILE_NAME)
    if os.path.exists(ml_project_path):
        with open(ml_project_path) as ml_project_file:
            yaml_obj = yaml.safe_load(ml_project_file.read())
    else:
        raise WorkflowException("MLProject.yaml config not found!")

    project_name = yaml_obj.get("name")
    if not project_name:
        project_name = None

    dependencies = yaml_obj.get("dependencies", {})
    python_interpreter = dependencies["python_interpreter"]
    if not python_interpreter:
        python_interpreter = None

    pip = dependencies["pip"]
    if not pip:
        pip = None

    pip_dependencies = yaml_obj.get("pip_dependencies", {})
    params = yaml_obj.get("params", {})
    entry_point = yaml_obj.get("entry_point")
    tags = yaml_obj.get("tags", {})

    return ProjectSpec(python_interpreter=python_interpreter, pip=pip, dependencies=dependencies,
                       pip_dependencies=pip_dependencies, params=params, entry_point=entry_point,
                       tags=tags, name=project_name)


class ProjectSpec(object):
    """A project specification loaded from an MLProject file in the passed-in directory."""

    def __init__(self, python_interpreter, pip, dependencies, pip_dependencies, params, entry_point, tags, name):
        self.python_interpreter = python_interpreter
        self.pip = pip
        self.dependencies = dependencies
        self.pip_dependencies = pip_dependencies
        self.params = params
        self.entry_point = entry_point
        self.tags = tags
        self.name = name


if __name__ == "__main__":
    load_project(os.path.abspath(os.path.dirname(__file__)))
