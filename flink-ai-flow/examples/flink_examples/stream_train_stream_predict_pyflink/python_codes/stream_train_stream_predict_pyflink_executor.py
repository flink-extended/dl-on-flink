import os
from ai_flow.util.time_utils import generate_time_str
from joblib import dump, load
from time import sleep
import time
from ai_flow.util.path_util import get_file_dir
from ai_flow import ExampleMeta, ModelMeta, ModelVersionStage
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import Table, ScalarFunction, DataTypes, CsvTableSink, WriteMode, \
    StreamTableEnvironment, EnvironmentSettings
from pyflink.table.descriptors import FileSystem, OldCsv, Schema
from pyflink.table.udf import udf
from python_ai_flow import ExampleExecutor
from typing import List
import threading
import pandas as pd
import ai_flow as af
from sklearn.neighbors import KNeighborsClassifier

from streamz import Stream

from flink_ai_flow.pyflink.user_define_executor import Executor, SourceExecutor, FlinkFunctionContext, SinkExecutor, \
    TableEnvCreator
from python_ai_flow import FunctionContext, Executor as PythonExecutor

EXAMPLE_COLUMNS = ['sl', 'sw', 'pl', 'pw', 'type']


class ReadTrainExample:
    class SourceThread(threading.Thread):
        def __init__(self, stream_uri):
            super().__init__()
            self.stream = Stream()
            self.stream_uri = stream_uri

        def run(self) -> None:
            for i in range(0, 1):
                train_data = pd.read_csv(self.stream_uri, header=0, names=EXAMPLE_COLUMNS)
                y_train = train_data.pop(EXAMPLE_COLUMNS[4])
                self.stream.emit((train_data.values, y_train.values))
                print('send-{}-example'.format(i))
                sleep(50)

    class LoadTrainExample(ExampleExecutor):
        def __init__(self):
            self.thread = None

        def setup(self, function_context: FunctionContext):
            example_meta: ExampleMeta = function_context.node_spec.example_meta
            self.thread = ReadTrainExample.SourceThread(example_meta.stream_uri)
            self.thread.start()

        def execute(self, function_context: FunctionContext, input_list: List) -> List:
            return [self.thread.stream]


class TrainModel(PythonExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        def sink(df):
            pass

        def train(df):
            x_train, y_train = df[0], df[1]
            sk_model = KNeighborsClassifier(n_neighbors=5)
            sk_model.fit(x_train, y_train)
            model_meta = function_context.node_spec.output_model
            model_path = get_file_dir(__file__) + '/saved_model'
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            model_timestamp = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
            model_path = model_path + '/' + model_timestamp
            dump(sk_model, model_path)
            af.register_model_version(model=model_meta, model_path=model_path)
            print('model update! {}'.format(model_meta.name))
            print(af.get_latest_generated_model_version(model_name=model_meta.name).model_path)
            print(af.get_latest_generated_model_version(model_name=model_meta.name).version)
            return df

        data: Stream = input_list[0]
        data.map(train).sink(sink)
        return []


class TestExampleReader(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        train_data = pd.read_csv(function_context.node_spec.example_meta.stream_uri, header=0, names=EXAMPLE_COLUMNS)
        y_train = train_data.pop(EXAMPLE_COLUMNS[4])
        return [[train_data, y_train]]


class ValidateModel(PythonExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        current_model_meta: ModelMeta = function_context.node_spec.model
        deployed_model_version = af.get_deployed_model_version(model_name=current_model_meta.name)

        new_model_meta = af.get_latest_generated_model_version(function_context.node_spec.model.name)
        print(new_model_meta.version)
        print(new_model_meta.model_path)
        if deployed_model_version is None:
            print("New Best Model Version {}".format(new_model_meta.version))
            af.update_model_version(model_name=current_model_meta.name,
                                    model_version=new_model_meta.version,
                                    current_stage=ModelVersionStage.VALIDATED)
            af.update_model_version(model_name=current_model_meta.name,
                                    model_version=new_model_meta.version,
                                    current_stage=ModelVersionStage.DEPLOYED)
        else:
            x_validate = input_list[0][0]
            y_validate = input_list[0][1]
            knn = load(new_model_meta.model_path)
            scores = knn.score(x_validate, y_validate)
            deployed_knn = load(deployed_model_version.model_path)
            deployed_scores = deployed_knn.score(x_validate, y_validate)
            stream_uri = af.get_artifact_by_name('validate_artifact').stream_uri
            with open(stream_uri, 'a') as f:
                f.write(
                    'deployed model version: {} scores: {}\n'.format(deployed_model_version.version, deployed_scores))
                f.write('generated model version: {} scores: {}\n'.format(new_model_meta.version, scores))
            print("New Best Model Version {} Old {}".format(new_model_meta.version, deployed_model_version.version))
            if scores >= deployed_scores:
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=deployed_model_version.version,
                                        current_stage=ModelVersionStage.DEPRECATED)
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=new_model_meta.version,
                                        current_stage=ModelVersionStage.VALIDATED)
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=new_model_meta.version,
                                        current_stage=ModelVersionStage.DEPLOYED)
        return []


class StreamTableEnvCreator(TableEnvCreator):

    def create_table_env(self):
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        stream_env.set_parallelism(1)
        t_env = StreamTableEnvironment.create(
            stream_env,
            environment_settings=EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build())
        statement_set = t_env.create_statement_set()
        t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)
        return stream_env, t_env, statement_set


class Source(SourceExecutor):
    def execute(self, function_context: FlinkFunctionContext) -> Table:
        print("### {} setup done2 for {}".format(self.__class__.__name__, "sads"))
        example_meta: ExampleMeta = function_context.get_example_meta()
        t_env = function_context.get_table_env()
        print(example_meta.batch_uri)
        t_env.connect(FileSystem().path(example_meta.batch_uri)) \
            .with_format(OldCsv()
                         .ignore_first_line()
                         .field(EXAMPLE_COLUMNS[0], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[1], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[2], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[3], DataTypes.FLOAT())) \
            .with_schema(Schema()
                         .field(EXAMPLE_COLUMNS[0], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[1], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[2], DataTypes.FLOAT())
                         .field(EXAMPLE_COLUMNS[3], DataTypes.FLOAT())) \
            .create_temporary_table('mySource')
        return t_env.from_path('mySource')


class Transformer(Executor):
    def __init__(self):
        super().__init__()
        self.model_name = None

    def setup(self, function_context: FunctionContext):
        self.model_name = function_context.node_spec.model.name

    def execute(self, function_context: FlinkFunctionContext, input_list: List[Table]) -> List[Table]:
        model_meta = af.get_deployed_model_version(self.model_name)
        model_path = model_meta.model_path
        print(model_path)
        clf = load(model_path)

        class Predict(ScalarFunction):
            def eval(self, sl, sw, pl, pw):
                records = [[sl, sw, pl, pw]]
                df = pd.DataFrame.from_records(records, columns=['sl', 'sw', 'pl', 'pw'])
                return clf.predict(df)[0]
        function_context.t_env.register_function('mypred',
                                                 udf(f=Predict(),
                                                     input_types=[DataTypes.FLOAT(), DataTypes.FLOAT(),
                                                                  DataTypes.FLOAT(), DataTypes.FLOAT()],
                                                     result_type=DataTypes.FLOAT()))
        print("-----")
        print(function_context.t_env.list_user_defined_functions())
        return [input_list[0].select("mypred(sl,sw,pl,pw)")]


class Sink(SinkExecutor):

    def execute(self, function_context: FlinkFunctionContext, input_table: Table) -> None:
        print("### {} setup done".format(self.__class__.__name__))
        table_env = function_context.get_table_env()
        table_env.register_table_sink("write_example", CsvTableSink(
            ['a'],
            [DataTypes.FLOAT()],
            function_context.get_example_meta().batch_uri,
            write_mode=WriteMode.OVERWRITE
        ))
        function_context.get_statement_set().add_insert("write_example", input_table)
        print("### {} table_env execute done {}".format(self.__class__.__name__,
                                                        function_context.get_example_meta().batch_uri))
