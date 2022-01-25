from pyflink.stream.functions.source import JavaSourceFunction
from pyflink.util.type_util import TypesUtil


class TFRSourceFunc(JavaSourceFunction):
    def __init__(self, paths, epochs, out_row_type, converters):
        src_func_clz_name = 'org.flinkextended.flink.tensorflow.hadoop.io.TFRToRowSourceFunc'
        src_func_clz = TypesUtil.class_for_name(src_func_clz_name)
        j_paths = TypesUtil._convert_py_list_to_java_array('java.lang.String', paths)
        j_converters = []
        for converter in converters:
            j_converters.append(converter.java_converter())
        j_converters = TypesUtil._convert_py_list_to_java_array(
            'org.flinkextended.flink.tensorflow.hadoop.io.TFRExtractRowHelper$ScalarConverter', j_converters)
        j_row_type = TypesUtil.to_java_sql_type(out_row_type)
        super(TFRSourceFunc, self).__init__(src_func_clz(j_paths, epochs, j_row_type, j_converters))
