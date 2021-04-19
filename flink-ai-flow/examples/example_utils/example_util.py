import os
from ai_flow.api.configuration import set_project_config_file
import types


def init_project_path(path):
    return os.path.abspath(path)


def get_project_config_file(path):
    return path + "/project.yaml"


def set_project_config(path):
    print("Project Config Path: " + get_project_config_file(path))
    set_project_config_file(get_project_config_file(path))


def get_parent_dir_name(path):
    return os.path.basename(os.path.dirname(path))



def list_all_fields(obj):
    for f in dir(obj):
        if str(f).startswith("_"):
            continue
        if isinstance(f, types.MethodType):
            continue
        print(str(f) + str(type(f)))
        if hasattr(obj, "__dict__") and f in obj.__dict__:
            list_all_fields(obj.__dict__[f])
    print("----------")
