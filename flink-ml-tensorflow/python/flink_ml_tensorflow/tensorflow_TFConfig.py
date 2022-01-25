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
        self._j_tf_config = None

    def java_config(self):
        if not self._j_tf_config:
            self._j_tf_config = get_gateway().jvm.org.flinkextended.flink.ml.tensorflow.client.TFConfig(self._num_worker,
                                                                                                        self._num_ps,
                                                                                                        self._properties,
                                                                                                        self._python_file,
                                                                                                        self._func,
                                                                                                        self._env_path)
        return self._j_tf_config

    def __eq__(self, other):
        return type(self) is type(other) \
               and self._num_worker == other._num_worker \
               and self._num_ps == other._num_ps \
               and self._properties == other._properties \
               and self._python_file == other._python_file \
               and self._func == other._func \
               and self._env_path == other._env_path
