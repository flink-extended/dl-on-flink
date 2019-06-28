import sys
import traceback
from flink_ml_framework.java_file import *


def map_func(context):
    print context
    sys.stdout.flush()
    bytes_recorder = BytesRecorder(context.from_java(), context.to_java())
    try:
        res = bytes_recorder.read_record()
        print "res", res
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
