import posixpath
import re


_VALID_PARAM_AND_METRIC_NAMES = re.compile(r"^[/\w.\- ]*$")

# Regex for valid run IDs: must be an alphanumeric string of length 1 to 256.
_RUN_ID_REGEX = re.compile(r"^[a-zA-Z0-9][\w\-]{0,255}$")

_EXPERIMENT_ID_REGEX = re.compile(r"^[a-zA-Z0-9][\w\-]{0,63}$")

_BAD_CHARACTERS_MESSAGE = (
    "Names may only contain alphanumerics, underscores (_), dashes (-), periods (.),"
    " spaces ( ), and slashes (/)."
)

MAX_PARAMS_TAGS_PER_BATCH = 100
MAX_METRICS_PER_BATCH = 1000
MAX_ENTITIES_PER_BATCH = 1000
MAX_BATCH_LOG_REQUEST_SIZE = int(1e6)
MAX_PARAM_VAL_LENGTH = 250
MAX_TAG_VAL_LENGTH = 5000
MAX_EXPERIMENT_TAG_KEY_LENGTH = 250
MAX_EXPERIMENT_TAG_VAL_LENGTH = 5000
MAX_ENTITY_KEY_LENGTH = 250


def bad_path_message(name):
    return (
        "Names may be treated as files in certain cases, and must not resolve to other names"
        " when treated as such. This name would resolve to '%s'"
    ) % posixpath.normpath(name)


def path_not_unique(name):
    norm = posixpath.normpath(name)
    return norm != name or norm == '.' or norm.startswith('..') or norm.startswith('/')

