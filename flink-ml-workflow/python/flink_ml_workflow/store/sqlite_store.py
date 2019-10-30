from python.flink_ml_workflow.store.abstract_store import AbstractStore
from python.flink_ml_workflow.vertex.example import *
from python.flink_ml_workflow.vertex.history import History, HistoryType
from python.flink_ml_workflow.vertex.model import ModelVersion, Model, ModelType
from python.flink_ml_workflow.vertex.project import Project, ProjectType
import sqlite3
import json
from python.flink_ml_workflow.proto import meta_data_pb2, meta_data_service_pb2


class LocalStore(AbstractStore):
    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir

    def get_model_by_id(self, model_id):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_proto where instanceId = ?', (model_id,))
        model_protos = [dict(row) for row in cursor.fetchall()]

        if len(model_protos) == 0:
            cursor.close()
            conn.close()
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in model_protos:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            modelType = row['modelType']
            uri = row['uri']

        cursor.execute('select * from model_version_proto where modelId = ?', (model_id,))
        model_versions = cursor.fetchall()
        version_list = []

        for version in model_versions:
            meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                       instanceId=version['instanceId'],
                                                       properties=json.loads(version['properties']))
            modelId = version['modelId']
            modelUri = version['modelUri']
            logUri = version['logUri']
            version = version['version']
            version_list.append(
                meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                logUri=logUri, version=version))

        model_proto = meta_data_pb2.ModelProto(meta=meta, modelType=modelType, uri=uri, versionList=version_list)
        model_response = meta_data_service_pb2.ModelResponse(
            header=meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok'),
            model=model_proto)
        cursor.close()
        conn.close()
        return model_response

    def get_model_by_name(self, name):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_proto where name = ?', (name,))
        model_protos = [dict(row) for row in cursor.fetchall()]
        if len(model_protos) == 0:
            cursor.close()
            conn.close()
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in model_protos:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            modelType = row['modelType']
            uri = row['uri']
            model_id = row['instanceId']

        cursor.execute('select * from model_version_proto where modelId = ?', (model_id,))
        model_versions = [dict(row) for row in cursor.fetchall()]
        version_list = []

        for version in model_versions:
            meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                       instanceId=version['instanceId'],
                                                       properties=json.loads(version['properties']))
            modelId = version['modelId']
            modelUri = version['modelUri']
            logUri = version['logUri']
            version = version['version']
            version_list.append(
                meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                logUri=logUri, version=version))

        model_proto = meta_data_pb2.ModelProto(meta=meta, modelType=modelType, uri=uri, versionList=version_list)
        model_response = meta_data_service_pb2.ModelResponse(
            header=meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok'),
            model=model_proto)
        cursor.close()
        conn.close()
        return model_response

    def list_model(self, page_size, offset):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_proto limit ?  offset ?', (page_size, offset))
        model_protos = [dict(row) for row in cursor.fetchall()]

        model_proto_list = []
        if len(model_protos) == 0:
            cursor.close()
            conn.close()
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in model_protos:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            modelType = row['modelType']
            uri = row['uri']
            cursor.execute('select * from model_version_proto where modelId = ?', (row['instanceId'],))
            model_versions = [dict(row) for row in cursor.fetchall()]
            version_list = []
            for version in model_versions:
                meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                           instanceId=version['instanceId'],
                                                           properties=json.loads(version['properties']))
                modelId = version['modelId']
                modelUri = version['modelUri']
                logUri = version['logUri']
                version = version['version']
                version_list.append(
                    meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                    logUri=logUri, version=version))

            model_proto = meta_data_pb2.ModelProto(meta=meta, modelType=modelType, uri=uri, versionList=version_list)
            model_proto_list.append(model_proto)
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ListModelResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                   message='ok'),
                                                       model=model_proto_list)

    def list_model_version(self, model_id, page_size, offset):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_version_proto where modelId = ? limit ? offset ?', (
            model_id, page_size, offset))
        model_versions = [dict(row) for row in cursor.fetchall()]
        if len(model_versions) == 0:
            cursor.close()
            conn.close()
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        version_list = []
        for version in model_versions:
            meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                       instanceId=version['instanceId'],
                                                       properties=json.loads(version['properties']))
            modelId = version['modelId']
            modelUri = version['modelUri']
            logUri = version['logUri']
            version = version['version']
            version_list.append(
                meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                logUri=logUri, version=version))
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ListModelVersionResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                          message='ok'),
                                                              modelVersion=version_list)

    def get_model_version_by_id(self, version_id):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_version_proto where instanceId =?', (version_id,))
        model_versions = [dict(row) for row in cursor.fetchall()]
        if len(model_versions) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message="no records")
        for version in model_versions:
            meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                       instanceId=version['instanceId'],
                                                       properties=json.loads(version['properties']))
            modelId = version['modelId']
            modelUri = version['modelUri']
            logUri = version['logUri']
            version = version['version']

            model_version_proto = meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                                  logUri=logUri, version=version)
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ModelVersionResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                      message='ok'),
                                                          modelVersion=model_version_proto)

    def get_model_version_by_version(self, version_name):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from model_version_proto where version = ?', (version_name,))
        model_versions = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(model_versions) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message="no records")
        for version in model_versions:
            meta_version = meta_data_pb2.MetaBaseProto(name=version['name'], typeId=version['typeId'],
                                                       instanceId=version['instanceId'],
                                                       properties=json.loads(version['properties']))
            modelId = version['modelId']
            modelUri = version['modelUri']
            logUri = version['logUri']
            version = version['version']

            model_version_proto = meta_data_pb2.ModelVersionProto(meta=meta_version, modelId=modelId, modelUri=modelUri,
                                                                  logUri=logUri, version=version)
        return meta_data_service_pb2.ModelVersionResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                      message='ok'),
                                                          modelVersion=model_version_proto)

    def save_model(self, model: Model):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        try:
            cursor.execute('insert into model_proto (name, properties, modelType, uri) values (?,?,?,?)',
                           (model.name, json.dumps(model.properties), model.model_type, model.uri))
            # cursor.execute("insert into model_proto (name,properties,modelType,uri) values (%s,%s,%s,%s)",
            #                (model.name, json.dumps(model.properties), model.model_type, model.uri))
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert failed')
        id = cursor.lastrowid
        for version in model.version_list:
            try:
                cursor.execute(
                    'insert into model_version_proto (properties,modelId,modelUri,logUri,version) values (?,?,?,?,?)',
                    (json.dumps(version.properties), id, version.model_uri,
                     version.log_uri, version.version))
                # cursor.execute(
                #     'insert into model_version_proto (properties,modelId,modelUri,logUri,version) values (%s,%s,%s,%s,%s)',
                #     (json.dumps(version.properties), id, version.model_uri,
                #      version.log_uri, version.version))
            except Exception as e:
                cursor.close()
                conn.close()
                print(e)
                return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        try:
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            cursor.close()
            conn.close()
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def save_model_version(self, model_version: ModelVersion):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        try:
            cursor.execute('insert into model_version_proto (properties,modelUri,logUri,version) values (?,?,?,?)',
                           (json.dumps(model_version.properties), model_version.model_uri, model_version.log_uri,
                            model_version.version))
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        conn.commit()
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def save_model_versions(self, version_list: list):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        for model_version in version_list:
            try:
                cursor.execute('insert into model_version_proto (properties,modelUri,logUri,version) values (?,?,?,?)',
                               (json.dumps(model_version.properties), model_version.model_uri, model_version.log_uri,
                                model_version.version))
            except (TypeError, sqlite3.IntegrityError) as e:
                cursor.close()
                conn.close()
                print(e)
                return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        conn.commit()
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def get_example_by_id(self, experiment_id):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from example_proto where instanceId=?', (experiment_id,))
        example_proto = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(example_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in example_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            example = meta_data_pb2.ExampleProto(meta=meta, supportType=row['supportType'],
                                                 schema=meta_data_pb2.SchemaProto(nameList=json.loads(row['nameList']),
                                                                                  typeList=json.loads(row['typeList'])),
                                                 exampleFormat=row['exampleFormat'], batchUri=row['batchUri'],
                                                 streamUri=row['streamUri'])
            return meta_data_service_pb2.ExampleResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         example=example)

    def get_example_by_name(self, experiment_name):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from example_proto where name=?', (experiment_name,))
        example_proto = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(example_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in example_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            example = meta_data_pb2.ExampleProto(meta=meta, supportType=row['supportType'],
                                                 schema=meta_data_pb2.SchemaProto(nameList=json.loads(row['nameList']),
                                                                                  typeList=json.loads(row['typeList'])),
                                                 exampleFormat=row['exampleFormat'], batchUri=row['batchUri'],
                                                 streamUri=row['streamUri'])
            return meta_data_service_pb2.ExampleResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         example=example)

    def list_example(self, page_size, offset):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from example_proto limit ? offset ?', (page_size, offset))
        example_protos = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(example_protos) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')

        example_list = []
        for row in example_protos:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            example_list.append(meta_data_pb2.ExampleProto(meta=meta, supportType=row['supportType'],
                                                           schema=meta_data_pb2.SchemaProto(
                                                               nameList=json.loads(row['nameList']),
                                                               typeList=json.loads(
                                                                   row['typeList'])),
                                                           exampleFormat=row['exampleFormat'], batchUri=row['batchUri'],
                                                           streamUri=row['streamUri']))
        return meta_data_service_pb2.ExampleListResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                         message='ok'),
                                                             examples=example_list)

    def save_example(self, example: Example):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        try:
            cursor.execute(
                'insert into example_proto (name, properties, supportType, nameList,typeList,exampleFormat,batchUri,streamUri) '
                'values (?,?,?,?,?,?,?,?)',
                (example.name, json.dumps(example.properties), example.example_type,
                 json.dumps(example.schema.name_list),
                 json.dumps(example.schema.type_list), example.example_format, example.batch_uri, example.stream_uri))
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert failed')
        conn.commit()
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def get_project_by_id(self, project_id):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from project_proto where instanceId=?', (project_id,))
        project_proto = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(project_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in project_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            project = meta_data_pb2.ProjectProto(meta=meta, projectType=row['projectType'],
                                                 uri=row['uri'], user=row['user'], password=row['password'])
            return meta_data_service_pb2.ProjectResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         project=project)

    def get_project_by_name(self, project_name):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from project_proto where name=?', (project_name,))
        project_proto = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(project_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in project_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            project = meta_data_pb2.ProjectProto(meta=meta, projectType=row['projectType'],
                                                 uri=row['uri'], user=row['user'], password=row['password'])
            return meta_data_service_pb2.ProjectResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         project=project)

    def save_project(self, project: Project):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        if project.properties == None:
            project.properties = {}
        try:
            cursor.execute(
                'insert into project_proto(name,properties,projectType,uri,"user",password) values (?,?,?,?,?,?)',
                (project.name, json.dumps(project.properties), project.project_type, project.uri,
                 project.user, project.password))
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        conn.commit()
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def list_projects(self, page_size, offset):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from project_proto limit ? offset ?', (page_size, offset))
        poject_protos = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(poject_protos) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        project_list = []
        for row in poject_protos:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            project = meta_data_pb2.ProjectProto(meta=meta, projectType=row['projectType'],
                                                 uri=row['uri'], user=row['user'], password=row['password'])
            project_list.append(project)
        return meta_data_service_pb2.ProjectListResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         Projects=project_list)

    def get_history_by_id(self, history_id):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from history_proto where instanceId=?', (history_id,))
        history_proto = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(history_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in history_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            history = meta_data_pb2.HistoryProto(meta=meta, type=row['type'],
                                                 referId=row['referId'], referName=row['referName'],
                                                 startTime=row['startTime'], endTime=row['endTime'],
                                                 uri=row['uri'])
            return meta_data_service_pb2.HistoryResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         history=history)

    def get_history_by_name(self, history_name):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from history_proto where name=?', (history_name,))
        history_proto = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(history_proto) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='no records')
        for row in history_proto:
            meta = meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                               properties=json.loads(row['properties']))
            history = meta_data_pb2.HistoryProto(meta=meta, type=row['type'],
                                                 referId=row['referId'], referName=row['referName'],
                                                 startTime=row['startTime'], endTime=row['endTime'],
                                                 uri=row['uri'])
            return meta_data_service_pb2.HistoryResponse(header=meta_data_service_pb2.ResponseHeader(returnCode=0,
                                                                                                     message='ok'),
                                                         history=history)

    def save_history(self, history: History):
        conn = sqlite3.connect('meta_data.db')
        cursor = conn.cursor()

        if history.properties == None:
            history.properties = {}
        try:
            cursor.execute(
                'insert into history_proto(name,properties,type,referId,referName,startTime,endTime,uri) values (?,?,?,?,?,?,?,?)',
                (history.name, json.dumps(history.properties), history.history_type,
                 history.refer_id, history.refer_name, history.start_time, history.end_time, history.uri))
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='insert fail')
        conn.commit()
        cursor.close()
        conn.close()
        return meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok')

    def list_history(self, page_size, offset):
        conn = sqlite3.connect('meta_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('select * from history_proto limit ? offset ?', (page_size, offset))
        histories = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if len(histories) == 0:
            return meta_data_service_pb2.ResponseHeader(returnCode=1, message='failed')
        history_list = []
        for row in histories:
            history_list.append(meta_data_pb2.HistoryProto(
                meta=meta_data_pb2.MetaBaseProto(name=row['name'], typeId=row['typeId'], instanceId=row['instanceId'],
                                                 properties=json.loads(row['properties'])),
                type=row['type'],
                referId=row['referId'],
                referName=row['referName'],
                startTime=row['startTime'],
                endTime=row['endTime'],
                uri=row['uri']))
        return meta_data_service_pb2.HistoryListResponse(
            header=meta_data_service_pb2.ResponseHeader(returnCode=0, message='ok'),
            histories=history_list)


if __name__ == '__main__':
    a = LocalStore(
        '/Users/yiwen/sourcecode/tywFlink/flink-ai-extended/flink-ml-workflow/python/flink_ml_workflow/store/meta_data.db')
    # print(a.get_model_by_id(1))
    # print(a.get_model_by_name('name'))
    # print(a.list_model(2, 3))
    # print(a.list_model_version(1, 2, 2))
    # print(a.get_model_version_by_id(9))
    # print(a.get_model_version_by_version('v100'))
    # version1 = ModelVersion(version='v1',
    #                         model_uri='aa/v1',
    #                         log_uri='aa/l1')
    # version2 = ModelVersion(version='v2',
    #                         model_uri='aa/v2',
    #                         log_uri='aa/l2')
    # model = Model(name="model0",
    #               model_type=ModelType.SAVED_MODEL,
    #               uri="aa")
    # model.add_version(version1)
    # model.add_version(version2)
    # print(a.save_model(model))
    # version1 = ModelVersion(version='v',
    #                         model_uri='aa/v1',
    #                         log_uri='aa/l1')
    # print(a.save_model_version(version1))
    # version1 = ModelVersion(version='v10',
    #                         model_uri='aa/v1',
    #                         log_uri='aa/l1')
    # version2 = ModelVersion(version='v20',
    #                         model_uri='aa/v2',
    #                         log_uri='aa/l2')
    # print(a.save_model_versions([version1, version2]))
    # print(a.get_example_by_id(1))
    # print(a.get_example_by_name('example'))
    # print(a.list_example(1, 2))
    # schema = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])
    # example = Example(name="example",
    #                   example_type=ExampleType.EXAMPLE_BOTH,
    #                   data_schema=schema,
    #                   example_format="CSV",
    #                   batch_uri="aa",
    #                   stream_uri="bb",
    #                   properties={'a': 'a'})
    # print(a.save_example(example))
    # print(a.get_project_by_id(3))
    # print(a.get_project_by_name('pro1'))
    # print(a.list_projects(1, 2))
    # project = Project(name="project",
    #                   project_type=ProjectType.GIT,
    #                   user="user",
    #                   password="password",
    #                   uri="./log",
    #                   properties={})
    # print(a.save_project(project))
    import time

    millis = int(round(time.time() * 1000))
    history = History(name="history",
                      history_type=HistoryType.EXECUTION,
                      start_time=millis,
                      end_time=millis + 5 * 1000,
                      uri="./log",
                      refer_name="execution")
    print(a.save_history(history))
    print(a.get_history_by_id(1))
    print(a.get_history_by_name('history1'))
    print(a.list_history(1, 0))
