from python.flink_ml_workflow.proto.meta_data_pb2 import *
from python.flink_ml_workflow.vertex.base_vertex import BaseVertex, RunMode
from python.flink_ml_workflow.vertex.example import *
from python.flink_ml_workflow.vertex.model import *


class Trainer(BaseVertex):

    def __init__(self,
                 name,
                 run_mode: RunMode,
                 input_example: Example,
                 output_model: Model,
                 output_model_version: ModelVersion,
                 py_main_script: str,
                 py_main_func_name: str,
                 py_package_uri: str = None,
                 py_scripts: list = None,
                 from_model: Model = None,
                 from_model_version: ModelVersion = None,
                 properties=None):
        super(Trainer, self).__init__(name, properties)
        self.run_mode = run_mode
        self.input_example = input_example
        self.output_model = output_model
        self.output_model_version = output_model_version
        self.py_main_script = py_main_script
        self.py_main_func_name = py_main_func_name
        self.py_package_uri = py_package_uri
        if py_scripts is None:
            self.py_scripts = list()
        else:
            self.py_scripts = py_scripts
        self.from_model = from_model
        self.from_model_version = from_model_version

    def to_proto(self):
        trainer_proto = TrainerProto()
        return self.set_proto(trainer_proto)

    def set_proto(self, trainer_proto):
        trainer_proto.meta.name = self.name
        for i in self.properties:
            trainer_proto.meta.properties[i] = self.properties[i]
        if self.run_mode == RunMode.STREAM:
            trainer_proto.runMode = RunModeProto.STREAM
        else:
            trainer_proto.runMode = RunModeProto.BATCH

        self.input_example.set_proto(trainer_proto.inputExample)
        self.output_model.set_proto(trainer_proto.outputModel)
        self.output_model_version.set_proto(trainer_proto.outputModelVersion)
        if self.from_model is not None:
            self.from_model.set_proto(trainer_proto.fromModel)
        if self.from_model_version is not None:
            self.from_model_version.set_proto(trainer_proto.fromModelVersion)
        if self.py_package_uri is not  None:
            trainer_proto.pyPackageUri = self.py_package_uri
        for i in self.py_scripts:
            trainer_proto.pyScripts.append(i)
        trainer_proto.pyMainScript = self.py_main_script
        trainer_proto.pyMainFuncName = self.py_main_func_name
        return trainer_proto


if __name__ == "__main__":
    schema = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])

    example = Example(name="example",
                      example_type=ExampleType.EXAMPLE_BOTH,
                      data_schema=schema,
                      example_format="CSV",
                      batch_uri="aa",
                      stream_uri="bb",
                      properties={'a': 'a'})

    version1 = ModelVersion(version='v1',
                            model_uri='aa/v1',
                            log_uri='aa/l1')
    version2 = ModelVersion(version='v2',
                            model_uri='aa/v2',
                            log_uri='aa/l2')
    model = Model(name="model",
                  model_type=ModelType.SAVED_MODEL,
                  uri="aa")
    model.add_version(version1)
    model.add_version(version2)

    output_m = Model(name="outputModel",
                     model_type=ModelType.SAVED_MODEL,
                     uri="bb")
    version3 = ModelVersion(version='v3',
                            model_uri='aa/v3',
                            log_uri='aa/l3')

    trainer = Trainer(name="trainer",
                      run_mode=RunMode.STREAM,
                      input_example=example,
                      output_model=output_m,
                      output_model_version=version3,
                      py_main_script="start.py",
                      py_main_func_name="aa")

    print(trainer.to_json())
