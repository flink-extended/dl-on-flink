from faker import Faker
import random
from flink_ml_workflow.store.mysql_store import *
from flink_ml_workflow.store.sqlite_store import *
import os

fake = Faker()
mysql = MysqlStore()
sqlite = LocalStore(os.getcwd() + 'meta_data.db')


def test_model():
    model = Model(name=fake.name(),
                  model_type=ModelType.SAVED_MODEL,
                  uri=fake.name())
    model_version_list = []
    for i in range(random.randint(0, 10)):
        model_version_list.append(ModelVersion(version=fake.name(),
                                               model_uri=fake.name(),
                                               log_uri=fake.name(),
                                               properties={fake.name(): fake.name()}))

    model_verison = ModelVersion(version='verison',
                                 model_uri=fake.name(),
                                 log_uri=fake.name())

    # print(mysql.save_model(model))
    # print(mysql.save_model_version(model_verison))
    # print(mysql.save_model_versions(model_version_list))
    #
    # print(mysql.get_model_by_id(1))
    # print(mysql.get_model_version_by_id(1))
    # print(mysql.list_model(1, 0))
    # print(mysql.list_model_version(1, 10, 0))
    # print(mysql.get_model_by_name('Gina Montgomery'))
    # print(mysql.get_model_version_by_version('verison'))

    print(sqlite.save_model(model))
    print(sqlite.save_model_version(model_verison))
    print(sqlite.save_model_versions(model_version_list))

    print(sqlite.get_model_by_id(1))
    print(sqlite.get_model_version_by_id(1))
    print(sqlite.list_model(1, 0))
    print(sqlite.list_model_version(1, 10, 0))
    print(sqlite.get_model_by_name('Gina Montgomery'))
    print(sqlite.get_model_version_by_version('verison'))


def test_example():
    for i in range(random.randint(0, 10)):
        schema = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])
        example = Example(name=fake.name(),
                          example_type=ExampleType.EXAMPLE_BOTH,
                          data_schema=schema,
                          example_format="CSV",
                          batch_uri=fake.name(),
                          stream_uri=fake.name(),
                          properties={fake.name(): fake.name()})
        # print(mysql.save_example(example))
        # print(mysql.get_example_by_id(1))
        # print(mysql.list_example(10, 2))

        print(sqlite.save_example(example))
        print(sqlite.get_example_by_id(1))
        print(sqlite.list_example(10, 2))


def test_history():
    for i in range(random.randint(0, 10)):
        import time

        millis = int(round(time.time() * 1000))
        history = History(name=fake.name(),
                          history_type=HistoryType.EXECUTION,
                          start_time=millis,
                          end_time=millis + 5 * 1000,
                          uri="./log",
                          refer_name="execution")
        # print(mysql.save_history(history))
        # print(mysql.get_history_by_id(3))
        # # print(mysql.get_history_by_name('history'))
        # print(mysql.list_history(10, 5))

        print(sqlite.save_history(history))
        print(sqlite.get_history_by_id(3))
        print(sqlite.get_history_by_name('history'))
        print(sqlite.list_history(10, 10))


def test_project():
    for i in range(random.randint(0, 10)):
        project = Project(name=fake.name(),
                          project_type=ProjectType.GIT,
                          user="user",
                          password="password",
                          uri="./log",
                          properties={})
        # print(mysql.save_project(project))
        # print(mysql.get_project_by_id(1))
        # print(mysql.get_project_by_name(''))
        # print(mysql.list_projects(10, 0))

        print(sqlite.save_project(project))
        print(sqlite.get_project_by_id(1))
        # print(sqlite.get_project_by_name(''))
        print(sqlite.list_projects(10, 0))


if __name__ == '__main__':
    # test_model()
    # test_example()
    # test_history()
    test_project()
