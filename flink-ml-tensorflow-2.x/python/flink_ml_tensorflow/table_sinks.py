from pyflink.java_gateway import get_gateway
from pyflink.util.type_util import TypesUtil
from pyflink.table.sinks import JavaTableSink
from sink_funcs import LogSink


class LogTableStreamSink(JavaTableSink):
    def __init__(self, sink_func=None):
        if sink_func is None:
            sink_func = LogSink()._j_sink_function
        sink_clz_name = 'org.flinkextended.flink.tensorflow.flink_op.sink.LogTableStreamSink'
        sink_clz = TypesUtil.class_for_name(sink_clz_name)
        super(LogTableStreamSink, self).__init__(sink_clz(sink_func))


class LogInferAccSink(LogTableStreamSink):
    def __init__(self):
        sink_func = get_gateway().jvm.org.flinkextended.flink.tensorflow.client.LogInferAccSink()
        super(LogInferAccSink, self).__init__(sink_func=sink_func)
