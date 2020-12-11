#
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
#
import codecs
import json
import os
import random
import time
import warnings
from multiprocessing import Pool
from subprocess import Popen

import joblib
import pandas as pd
from ai_flow.common.path_util import get_file_dir
from cloudpickle import cloudpickle
from joblib._parallel_backends import SafeFunction
from joblib.parallel import AutoBatchingMixin, ParallelBackendBase, register_parallel_backend, SequentialBackend
from pyflink.find_flink_home import _find_flink_home
from pyflink.table import BatchTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.table.descriptors import FileSystem, OldCsv, Schema
from pyflink.table.udf import udf

'''
Joblib Flink backend implementation.
'''


def register():
    """
    Register Flink backend into Joblib called with parallel_backend('flink').
    """

    register_parallel_backend('flink', FlinkBackend)


class FlinkBackend(ParallelBackendBase, AutoBatchingMixin):
    """ParallelBackend which execute batches on Flink backend.

    `FlinkBackend` backend launches one Flink job for each task batch. Multiple Flink job will run parallelly.

    Each task batch run inside one Flink task on worker node, and execute through `SequentialBackend`.
    """

    def __init__(self, mode='local', job_manager='localhost:8081', python_path='/usr/bin/python', **backend_args):
        super(FlinkBackend, self).__init__(**backend_args)
        self.mode = mode
        self._job_manager = job_manager
        self._python_path = python_path
        self._jobs = list()
        self._pool = None
        self._n_jobs = None

    def _get_pool(self):
        if self._pool is None:
            self._pool = Pool(self._n_jobs)
        return self._pool

    def _cancel_jobs(self):
        for job in self._jobs:
            cancel_stdout = '{}/cancel_{}_stdout.log'.format(get_file_dir(__file__), job)
            cancel_stderr = '{}/cancel_{}_stderr.log'.format(get_file_dir(__file__), job)
            with open(cancel_stdout, 'a') as out, open(cancel_stderr, 'a') as err:
                # execute `flink cancel <jobID>` to cancel batch job
                Popen(args='{}/bin/flink cancel {}'.format(_find_flink_home(), job), shell=True, stdout=out, stderr=err)

    @staticmethod
    def _local_execute_func(exec_func, write_func, pickle_func, python_path):
        table_env = BatchTableEnvironment.create(
            environment_settings=EnvironmentSettings.new_instance().use_blink_planner().in_batch_mode().build())
        table_env.get_config().get_configuration().set_string('parallelism.default', '1')
        table_env.get_config().set_python_executable(python_path)
        table_env.register_function(exec_func, udf(lambda _: pickle_func, DataTypes.BIGINT(), DataTypes.STRING()))
        table_env.connect(FileSystem().path(write_func)) \
            .with_format(OldCsv().field('func', DataTypes.STRING())) \
            .with_schema(Schema().field('func', DataTypes.STRING())) \
            .create_temporary_table(exec_func)
        table = table_env.from_elements([(1, 'Joblib')])
        table.select('{}(_1)'.format(exec_func)).insert_into(exec_func)
        table_env.execute(exec_func)
        # decode execution result from table sink file.
        execute_result = cloudpickle.loads(
            codecs.decode(pd.DataFrame(pd.read_csv(write_func))[0:].columns[0].encode(), 'base64'))
        # remove table sink file to clear ineffective files.
        os.remove(write_func)
        return execute_result

    @staticmethod
    def _remote_execute_func(exec_func, write_func, exec_dict, jm, py):
        func_stdout = '{}/exec_{}_stdout.log'.format(get_file_dir(__file__), exec_func)
        func_stderr = '{}/exec_{}_stderr.log'.format(get_file_dir(__file__), exec_func)
        with open(func_stdout, 'a') as out, open(func_stderr, 'a') as err:
            # execute `flink run -m <remote> -py function.py` to submit batch job
            submitted_process = Popen(
                args="{}/bin/flink run -m {} -py {}/exec_function.py -pyexec {} {} {} '{}'".format(_find_flink_home(),
                                                                                                   jm, get_file_dir(
                        __file__),
                                                                                                   py, exec_func,
                                                                                                   write_func,
                                                                                                   json.dumps(
                                                                                                       exec_dict)),
                shell=True, stdout=out, stderr=err)
            submitted_process.wait()
        # decode execution result from table sink file.
        execute_result = cloudpickle.loads(
            codecs.decode(pd.DataFrame(pd.read_csv(write_func))['func'].values[0].encode(), 'base64'))
        # remove table sink file to clear ineffective files.
        os.remove(write_func)
        return execute_result

    def effective_n_jobs(self, n_jobs):
        cpu_count = joblib.cpu_count()
        if n_jobs is None:
            n_jobs = 1
        elif n_jobs == -1:
            n_jobs = cpu_count
        if n_jobs > cpu_count:
            warnings.warn(
                'User-specified n_jobs ({n}) is greater than the count of cpu ({c}) this cluster can run now.'
                    .format(n=n_jobs, c=cpu_count))
        return n_jobs

    def apply_async(self, func, callback=None):
        exec_func = 'func{}{}'.format(round(time.time()), random.randint(0, round(time.time())))
        pickle_func = codecs.encode(cloudpickle.dumps(func()), 'base64').decode()
        write_func = '{}/{}.csv'.format(get_file_dir(__file__), exec_func)
        if self.mode == 'local':
            return self._get_pool().apply_async(SafeFunction(self._local_execute_func),
                                                args=[exec_func, write_func, pickle_func, self._python_path, ],
                                                callback=callback)
        else:
            exec_dict = {exec_func: pickle_func}
            return self._get_pool().apply_async(SafeFunction(self._remote_execute_func),
                                                args=[exec_func, write_func, exec_dict, self._job_manager,
                                                      self._python_path, ],
                                                callback=callback)

    def configure(self, n_jobs=1, parallel=None, prefer=None, require=None, **backend_args):
        n_jobs = self.effective_n_jobs(n_jobs)
        self._n_jobs = n_jobs
        return n_jobs

    def terminate(self):
        self._cancel_jobs()

    def abort_everything(self, ensure_ready=True):
        self._cancel_jobs()
        if ensure_ready:
            self.configure(n_jobs=self.parallel.n_jobs, parallel=self.parallel, **self.parallel._backend_args)

    def get_nested_backend(self):
        nesting_level = getattr(self, 'nesting_level', 0) + 1
        return SequentialBackend(nesting_level=nesting_level), None
