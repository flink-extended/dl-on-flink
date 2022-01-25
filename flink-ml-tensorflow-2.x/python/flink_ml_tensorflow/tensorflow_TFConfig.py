from pyflink.java_gateway import get_gateway


class TFConfig(object):

    def __init__(self, num_worker, num_ps, properties, python_file, func, env_path):
        """

        :param num_worker: the number of TF workers
        :param num_ps: the number of TF PS
        :param properties: TF properties
        :param python_file: the python file, the entry python file
        :param func: the entry function name in the first python file
        :param env_path: the path of env
        """
        self._num_worker = num_worker
        self._num_ps = num_ps
        self._properties = properties
        self._python_file = python_file
        self._func = func
        self._env_path = env_path

    def java_config(self):
        return get_gateway().jvm.org.flinkextended.flink.ml.tensorflow.client.TFConfig(self._num_worker,
                                                                                 self._num_ps,
                                                                                 self._properties,
                                                                                 self._python_file,
                                                                                 self._func,
                                                                                 self._env_path)
