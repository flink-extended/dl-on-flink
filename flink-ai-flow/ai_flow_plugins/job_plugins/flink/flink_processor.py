# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from abc import abstractmethod
from typing import List, Dict, Text, Optional, Union

from pyflink.table.udf import UserDefinedScalarFunctionWrapper

from ai_flow import DatasetMeta
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.util import json_utils
from pyflink.dataset import ExecutionEnvironment
from pyflink.table import TableEnvironment, StatementSet, Table


class ExecutionContext(json_utils.Jsonable):
    """
    ExecutionContext contains job execution information(job_execution_info),
    AINode node configuration parameters(config), ExecutionEnvironment, TableEnvironment and StatementSet.
    ExecutionContext is passed as a parameter to the process function of FlinkPythonProcessor.
    """

    def __init__(self,
                 job_execution_info: JobExecutionInfo,
                 config: Dict,
                 execution_env: ExecutionEnvironment,
                 table_env: TableEnvironment,
                 statement_set: StatementSet
                 ):
        self._job_execution_info = job_execution_info
        self._config: Dict = config
        self._execution_env = execution_env
        self._table_env = table_env
        self._statement_set = statement_set

    @property
    def job_execution_info(self) -> JobExecutionInfo:
        return self._job_execution_info

    @property
    def name(self):
        return self._config['name']

    @property
    def node_type(self):
        return self._config['node_type']

    @property
    def config(self) -> Dict:
        return self._config

    @property
    def execution_env(self) -> ExecutionEnvironment:
        return self._execution_env

    @property
    def table_env(self) -> TableEnvironment:
        return self._table_env

    @property
    def statement_set(self) -> StatementSet:
        return self._statement_set


class FlinkPythonProcessor(object):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Process method for user-defined function. User write their logic in this method.
        """
        pass

    def open(self, execution_context: ExecutionContext):
        """
        Open method for user-defined function. It can be used as a preparation stage before the process function.
        By default, this method does nothing.
        """
        pass

    def close(self, execution_context: ExecutionContext):
        """
        Close method for user-defined function. It can be used as a cleanup phase after the process function.
        By default, this method does nothing.
        """
        pass


class FlinkJavaProcessor(object):
    """
    FlinkJavaProcessor is the processor of flink java jobs.
    """

    def __init__(self,
                 entry_class: Optional[Text],
                 main_jar_file: Text,
                 args: List[Text] = None) -> None:
        """
        :param entry_class: Flink job entry class.
        :param main_jar_file: Flink job jar package name.
        :param args: The args are user-defined parameters.
        """
        super().__init__()
        self.entry_class: Text = entry_class
        self.main_jar_file: Text = main_jar_file
        self.args = args


class UDFWrapper(object):
    """
    A wrapper for flink udf, which will be utilized by FlinkSqlProcessor to pass user-defined functions(udf and udtf).
    """
    def __init__(self, name, func: Union[str, UserDefinedScalarFunctionWrapper]):
        """
       :param name: The name of user-defined functions which will be registered in the table env.
       :param func: Thr user-defined function. For python, it is the python user-defined function to register. For java,
        it is the java full qualified class name of the function to register.
       """
        self.name = name
        self.func = func

    def is_java_udf(self):
        return type(self.func) == str


class FlinkSqlProcessor(FlinkPythonProcessor):
    """
    FlinkSqlProcessor is the processor of flink sql jobs based on pyflink.
    """
    @abstractmethod
    def sql_statements(self, execution_context: ExecutionContext) -> List[str]:
        """
        The user should override this method to define their own sql statements. Multiple insertions in a job will be
        added into one same statement set.
        
        For the processor in :py:func:`~ai_flow.api.ops.read_dataset` or :py:func:`~ai_flow.api.ops.write_dataset`, 
        this method should return at most one DDL(i.e. CREATE statement) for table source or table sink and the DDL
        should be consistent with the dataset_info in the :py:func:`~ai_flow.api.ops.read_dataset` or 
        :py:func:`~ai_flow.api.ops.write_dataset` (i.e. dataset_info.data_format should be equal to the 'format' option 
        in DDL if it is defined.). 
        
        If multiple table sinks are required, users can call multiple :py:func:`~ai_flow.api.ops.write_dataset` or use 
        single :py:func:`~ai_flow.api.ops.user_define_operation` with multiple DDL. 
        

        :param execution_context: The :class:`~ai_flow_plugins.job_plugins.flink.flink_processor.ExecutionContext` of
        the processor
        :rtype List[str]: A list of sql statement. Each element should be a DDL/DML/DQL statement.
        """
        pass

    @abstractmethod
    def udf_list(self, execution_context: ExecutionContext) -> List[UDFWrapper]:
        """
        The user should override this method to register user-defined functions(udf or udtf). 

        :param execution_context: The :class:`~ai_flow_plugins.job_plugins.flink.flink_processor.ExecutionContext` of
        the processor
        :rtype List[UDFWrapper]: A list of :classs:`ai_flow_plugins.job_plugins.flink.flink_processor.UDFWrapper`. 
        """
        pass

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        The method will register udfs defined in :py:func:`~ai_flow_plugins.job_plugins.flink.flink_processor.FlinkSqlProcessor.udf_list`
        and execute sql statements in :py:func:`~ai_flow_plugins.job_plugins.flink.flink_processor.FlinkSqlProcessor.sql_statements`.
        """
        _sql_statements = self.sql_statements(execution_context)
        if _sql_statements is None or len(_sql_statements) == 0:
            raise Exception("The sql_statements() cannot be None or empty.")
        sql_statements = [statement.strip() for statement in _sql_statements]
        table_env = execution_context.table_env
        statement_set = execution_context.statement_set
        _udfs = self.udf_list(execution_context)
        if _udfs is not None:
            for udf in _udfs:
                if udf.is_java_udf():
                    table_env.register_java_function(udf.name, udf.func)
                else:
                    table_env.register_function(udf.name, udf.func)

        for sql_statement in sql_statements:
            if sql_statement.lower().startswith('insert'):
                statement_set.add_insert_sql(sql_statement)
            elif sql_statement.lower().startswith('create'):
                # Check if users' DDL are consistent with info they provide in the
                # :py:class:`ai_flow.meta.dataset_meta.DatasetMeta`
                if execution_context.node_type == 'read_dataset' or execution_context.node_type == 'write_dataset':
                    dataset_meta: DatasetMeta = execution_context.config['dataset']
                    if not _validate_create_statement(sql_statement, dataset_meta):
                        raise Exception("'format' option in CREATE statement is inconsistent with the attached "
                                        "dataset! The registered format of the dataset is {}", dataset_meta.data_format)

                table_env.execute_sql(sql_statement)
            else:
                table_env.execute_sql(sql_statement)
        return []


def _check_options_in_sql(stmt, option_name, target_value):
    if target_value is None:
        return True
    words = stmt.split()
    for i in range(len(words)):
        if words[i] == option_name and i + 1 < len(words) and words[i + 1] == '=':
            if i + 2 < len(words) and target_value.lower() != words[i + 2].replace("'", '').lower():
                return False
    return True


def _validate_create_statement(stmt, dataset_meta: DatasetMeta):
    required_format = dataset_meta.data_format
    required_connector = None if dataset_meta.properties is None else dataset_meta.properties.get('connector')
    return _check_options_in_sql(stmt, "'format'", required_format) and \
           _check_options_in_sql(stmt, "'connector'", required_connector)
