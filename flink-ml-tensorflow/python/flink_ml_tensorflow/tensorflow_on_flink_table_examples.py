import os

from pyflink.datastream.stream_execution_environment import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.table.table import TableSchema
from tensorflow_on_flink_table import train,inference
from tensorflow_on_flink_tfconf import TFCONSTANS
from tensorflow_on_flink_mlconf import MLCONSTANTS
from pyflink.table.sources import CsvTableSource
from pyflink.table.types import DataTypes


class tableTest(object):

    @staticmethod
    def addTrainTable():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        table_env = StreamTableEnvironment.create(stream_env)
        work_num = 2
        ps_num = 1
        python_file = os.getcwd() + "/../../src/test/python/add.py"
        func = "map_func"
        property = None
        env_path = None
        input_tb = None
        output_schema = None

        train(work_num,ps_num,python_file,func,property,env_path,None,None,stream_env,table_env,input_tb,output_schema)
        # inference(work_num, ps_num, python_file, func, property, env_path, None, None, stream_env, table_env, input_tb,output_schema)

    @staticmethod
    def addTrainChiefAloneTable():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        table_env = StreamTableEnvironment.create(stream_env)
        work_num = 2
        ps_num = 1
        python_file = os.getcwd() + "/../../src/test/python/add.py"
        func = "map_func"
        property = {}
        property[TFCONSTANS.TF_IS_CHIEF_ALONE] = "ture"
        env_path = None
        input_tb = None
        output_schema = None

        train(work_num,ps_num,python_file,func,property,env_path,None,None,stream_env,table_env,input_tb,output_schema)
        # inference(work_num, ps_num, python_file, func, property, env_path, None, None, stream_env, table_env, input_tb,output_schema)

    @staticmethod
    def inputOutputTable():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        table_env = StreamTableEnvironment.create(stream_env)
        work_num = 2
        ps_num = 1
        python_file = os.getcwd() + "/../../src/test/python/input_output.py"
        property = {}
        func = "map_func"
        env_path = None
        property[MLCONSTANTS.ENCODING_CLASS] = "com.alibaba.flink.ml.operator.coding.RowCSVCoding"
        property[MLCONSTANTS.DECODING_CLASS] = "com.alibaba.flink.ml.operator.coding.RowCSVCoding"
        inputSb = "INT_32" + "," + "INT_64" + "," + "FLOAT_32" + "," + "FLOAT_64" + "," + "STRING"
        property["SYS:csv_encode_types"] = inputSb
        property["SYS:csv_decode_types"] = inputSb
        source_file = os.getcwd() + "/../../src/test/resources/input.csv"
        table_source = CsvTableSource(source_file,
                                      ["a","b","c","d","e"],
                                      [DataTypes.INT(),
                                       DataTypes.INT(),
                                       DataTypes.FLOAT(),
                                       DataTypes.DOUBLE(),
                                       DataTypes.STRING()])
        table_env.register_table_source("source",table_source)
        input_tb = table_env.scan("source")
        output_schema = TableSchema(["a","b","c","d","e"],
                                    [DataTypes.INT(),
                                     DataTypes.INT(),
                                     DataTypes.FLOAT(),
                                     DataTypes.DOUBLE(),
                                     DataTypes.STRING()]
                                    )
        train(work_num,ps_num,python_file,func,property,env_path,None,None,stream_env,table_env,input_tb,output_schema)
        # inference(work_num, ps_num, python_file, func, property, env_path, None, None, stream_env, table_env, input_tb,output_schema)




    @staticmethod
    def testWorkerZeroFinish():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        table_env = StreamTableEnvironment.create(stream_env)
        work_num = 3
        ps_num = 2
        python_file = os.getcwd() + "/../../src/test/python/worker_0_finish.py"
        func = "map_func"
        property = None
        env_path = None
        input_tb = None
        output_schema = None

        train(work_num,ps_num,python_file,func,property,env_path,None,None,stream_env,table_env,input_tb,output_schema)
        # inference(work_num, ps_num, python_file, func, property, env_path, None, None, stream_env, table_env, input_tb,output_schema)


if __name__ == '__main__':
    tableTest.addTrainTable()
    tableTest.addTrainChiefAloneTable()
    tableTest.testWorkerZeroFinish()
    tableTest.inputOutputTable()