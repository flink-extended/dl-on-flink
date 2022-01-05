import time
from tensorflow_on_flink import tensorflow_on_flink_table
from tensorflow_on_flink import tensorflow_on_flink_datastream
from tensorflow_on_flink.tfrecord_table_source import ScalarConverter
from tensorflow_on_flink.tfrecord_table_source import TFRTableSource
from tensorflow_on_flink.table_sinks import LogTableStreamSink, LogInferAccSink
from tensorflow_on_flink.tfrecord_source_func import TFRSourceFunc
from tensorflow_on_flink.sink_funcs import LogSink
import mnist_dist
import mnist_dist_with_input
import mnist_table_inference
from pyflink.environment import StreamExecutionEnvironment
from pyflink.table.table_environment import TableEnvironment
from pyflink.table.table_schema import TableSchema
from pyflink.util.type_util import TypesUtil
from pyflink.table.functions import JavaTableFunction
from pyflink.sql.data_type import StringType, IntegerType, RowType, LongType
from tensorflow_on_flink.tensorflow_on_flink_conf import *
import os


def get_root_path():
    return get_gateway().jvm.org.flinkextended.flink.tensorflow.util.TestUtil.getProjectRootPath()


export_path = get_root_path() + '/examples/target/export/0'


def build_props(version=None):
    root_path = get_root_path()
    if version is None:
        version = str(int(round(time.time() * 1000)))
    props = {"batch_size": "32", "input": root_path + "/examples/target/data/train/", "epochs": "1",
             "checkpoint_dir": root_path + "/examples/target/ckpt/" + version,
             "export_dir": root_path + "/examples/target/export/" + version}
    return props


def prep_data():
    get_gateway().jvm.org.flinkextended.flink.tensorflow.mnist.MnistDataUtil.prepareData()


def start_zk_server(port=2181):
    return get_gateway().jvm.org.apache.curator.test.TestingServer(port, True)


def generate_model():
    if not os.path.exists(export_path):
        tensorflow_on_flink_table.train(num_worker=1, num_ps=1, func=mnist_dist.map_fun, properties=build_props('0'))


def table_no_input():
    prep_data()
    testing_server = start_zk_server()
    tensorflow_on_flink_table.train(num_worker=1, num_ps=1, func=mnist_dist.map_fun, properties=build_props(),
                                    zk_conn="localhost:2181")
    testing_server.stop()


def datastream_no_input():
    prep_data()
    testing_server = start_zk_server()
    tensorflow_on_flink_datastream.train(num_worker=1, num_ps=1, func=mnist_dist.map_fun, properties=build_props())
    testing_server.stop()


def datastream_inference_input():
    prep_data()
    testing_server = start_zk_server()
    generate_model()
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    test_data_path = "file://" + get_root_path() + "/examples/target/data/test/"
    paths = [test_data_path + "0.tfrecords", test_data_path + "1.tfrecords"]
    src_row_type = RowType([StringType(), IntegerType()], ["image_raw", "label"])
    input_ds = stream_env.add_source(source_func=TFRSourceFunc(paths=paths, epochs=1, out_row_type=src_row_type,
                                                               converters=[ScalarConverter.FIRST,
                                                                           ScalarConverter.ONE_HOT]))
    input_ds.set_parallelism(len(paths))
    out_row_type = RowType([IntegerType(), IntegerType()], ['label_org', 'predict_label'])
    output_ds = tensorflow_on_flink_datastream.inference(num_worker=1, func=mnist_table_inference.map_fun,
                                                         properties=build_props('0'), stream_env=stream_env,
                                                         input_ds=input_ds, output_row_type=out_row_type)
    output_ds.add_sink(LogSink())
    stream_env.execute()
    testing_server.stop()


def datastream_with_input():
    prep_data()
    testing_server = start_zk_server()
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    train_data_path = "file://" + get_root_path() + "/examples/target/data/train/"
    paths = [train_data_path + "0.tfrecords", train_data_path + "1.tfrecords"]
    src_row_type = RowType([StringType(), IntegerType()], ["image_raw", "label"])
    input_ds = stream_env.add_source(TFRSourceFunc(paths=paths, epochs=1, out_row_type=src_row_type,
                                                   converters=[ScalarConverter.FIRST,
                                                               ScalarConverter.ONE_HOT]))
    input_ds.set_parallelism(len(paths))
    tensorflow_on_flink_datastream.train(num_worker=1, num_ps=1, func=mnist_dist_with_input.map_fun,
                                         properties=build_props(), input_ds=input_ds, stream_env=stream_env)
    stream_env.execute()
    testing_server.stop()


def table_with_input():
    prep_data()
    testing_server = start_zk_server()
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    table_env = TableEnvironment.get_table_environment(stream_env)
    stream_env.set_parallelism(2)
    train_data_path = "file://" + get_root_path() + "/examples/target/data/train/"
    paths = [train_data_path + "0.tfrecords", train_data_path + "1.tfrecords"]
    out_row_type = RowType([StringType(), IntegerType()], ["image_raw", "label"])
    table_src = TFRTableSource(paths=paths, epochs=1, out_row_type=out_row_type,
                               converters=[ScalarConverter.FIRST, ScalarConverter.ONE_HOT])
    input_table = table_src.register_table(table_env=table_env)
    tensorflow_on_flink_table.train(num_worker=1, num_ps=1, func=mnist_dist_with_input.map_fun,
                                    properties=build_props(), stream_env=stream_env,
                                    table_env=table_env, input_table=input_table)
    table_env.generate_stream_graph()
    stream_env.execute()
    testing_server.stop()


def table_inference():
    prep_data()
    testing_server = start_zk_server()
    generate_model()
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    table_env = TableEnvironment.get_table_environment(stream_env)
    stream_env.set_parallelism(2)
    test_data_path = "file://" + get_root_path() + "/examples/target/data/test/"
    paths = [test_data_path + "0.tfrecords", test_data_path + "1.tfrecords"]
    src_row_type = RowType([StringType(), IntegerType()], ["image_raw", "label"])
    table_src = TFRTableSource(paths=paths, epochs=1, out_row_type=src_row_type,
                               converters=[ScalarConverter.FIRST, ScalarConverter.ONE_HOT])
    input_table = table_src.register_table(table_env=table_env)
    builder = TableSchema.Builder()
    builder.column(name='label_org', data_type=IntegerType()).column(name='predict_label', data_type=IntegerType())
    output_schema = builder.build()
    output_table = tensorflow_on_flink_table.inference(num_worker=2, func=mnist_table_inference.map_fun,
                                                       properties=build_props('0'), stream_env=stream_env,
                                                       table_env=table_env, input_table=input_table,
                                                       output_schema=output_schema)
    output_table.write_to_sink(LogTableStreamSink())
    table_env.generate_stream_graph()
    stream_env.execute()
    testing_server.stop()


def java_inference_extract_func():
    func_clz_name = 'org.flinkextended.flink.tensorflow.client.MnistTFRExtractRowForJavaFunction'
    func_clz = TypesUtil.class_for_name(func_clz_name)
    return JavaTableFunction(func_clz())


def table_java_inference():
    prep_data()
    testing_server = start_zk_server()
    generate_model()
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    table_env = TableEnvironment.get_table_environment(stream_env)
    stream_env.set_parallelism(2)
    train_data_path = "file://" + get_root_path() + "/examples/target/data/test/"
    paths = [train_data_path + "0.tfrecords", train_data_path + "1.tfrecords"]
    src_row_type = RowType([StringType(), IntegerType()], ["image_raw", "label"])
    table_src = TFRTableSource(paths=paths, epochs=1, out_row_type=src_row_type,
                               converters=[ScalarConverter.FIRST, ScalarConverter.ONE_HOT])
    tfr_tbl_name = "tfr_input_table"
    table_env.register_table_source(tfr_tbl_name, table_src)
    ext_func_name = "tfr_extract"
    table_env.register_function(ext_func_name, java_inference_extract_func())
    out_cols = 'image,org_label'
    in_cols = ','.join(src_row_type.fields_names)
    extracted = table_env.sql_query(
        'select {} from {}, LATERAL TABLE({}({})) as T({})'.format(out_cols, tfr_tbl_name, ext_func_name, in_cols,
                                                                   out_cols))
    builder = TableSchema.Builder()
    builder.column(name='real_label', data_type=LongType()).column(name='predicted_label', data_type=LongType())
    output_schema = builder.build()
    props = build_props('0')
    props[TF_INFERENCE_EXPORT_PATH] = export_path
    props[TF_INFERENCE_INPUT_TENSOR_NAMES] = 'image'
    props[TF_INFERENCE_OUTPUT_TENSOR_NAMES] = 'prediction'
    props[TF_INFERENCE_OUTPUT_ROW_FIELDS] = ','.join(['org_label', 'prediction'])
    output_table = tensorflow_on_flink_table.inference(num_worker=2, properties=props, stream_env=stream_env,
                                                       table_env=table_env, input_table=extracted,
                                                       output_schema=output_schema)
    output_table.write_to_sink(LogInferAccSink())
    table_env.generate_stream_graph()
    stream_env.execute()
    testing_server.stop()


if __name__ == "__main__":
    table_no_input()
    datastream_no_input()
    datastream_with_input()
    table_with_input()
    table_inference()
    table_java_inference()
    datastream_inference_input()
