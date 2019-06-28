import sys
import traceback
from flink_ml_framework.java_file import *


def map_func(context):
    print context
    sys.stdout.flush()
    bytes_recorder = BytesRecorder(context.from_java(), context.to_java())
    try:
        while True:

            data = bytes_recorder.read_record()
            print context.index, "data:", data
            sys.stdout.flush()
            res = bytes_recorder.write_record(data)
            print context.index, "res:", res
            sys.stdout.flush()
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
