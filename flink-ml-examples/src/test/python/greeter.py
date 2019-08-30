from __future__ import print_function
import sys


def map_func(context):
    print('hello from greeter')
    print('index:', context.get_index())
    sys.stdout.flush()
