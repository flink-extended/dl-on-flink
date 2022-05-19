#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import print_function
# A quick fix to run TF 1.X code in TF 2.X, we may want to properly migrate the Python script to TF 2.X API.
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import sys
import time
from tensorflow.python.summary.writer.writer_cache import FileWriterCache as SummaryWriterCache
from dl_on_flink_tensorflow import tensorflow_on_flink_ops as tff_ops
from dl_on_flink_tensorflow.tensorflow_context import TFContext
import traceback


def map_func(context):
    print(tf.__version__)
    sys.stdout.flush()
    tf_context = TFContext(context)
    job_name = tf_context.get_node_type()
    index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster_config()
    print (cluster_json)
    sys.stdout.flush()
    cluster = tf.train.ClusterSpec(cluster=cluster_json)
    server = tf.train.Server(cluster, job_name=job_name, task_index=index)
    sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False,
                                 device_filters=["/job:ps", "/job:worker/task:%d" % index])
    if 'ps' == job_name:
        from time import sleep
        while True:
            sleep(1)
    else:
        with tf.device(tf.train.replica_device_setter(worker_device='/job:worker/task:' + str(index), cluster=cluster)):
            record_defaults = [[9], [tf.constant(value=9, dtype=tf.int64)], [9.0],
                               [tf.constant(value=9.0, dtype=tf.float64)], ["9.0"]]
            dataset = tf_context.get_tfdataset_from_flink(buffer_size=0)
            dataset = dataset.map(lambda record: tf.decode_csv(record, record_defaults=record_defaults))
            dataset = dataset.batch(3)
            iterator = tf.data.make_one_shot_iterator(dataset)
            input_records = iterator.get_next()

            global_step = tf.train.get_or_create_global_step()
            global_step_inc = tf.assign_add(global_step, 1)
            out = tff_ops.encode_csv(input_list=input_records)
            fw = tff_ops.FlinkTFRecordWriter(address=context.to_java())
            w = fw.write([out])
            is_chief = (index == 0)
            t = time.time()
            try:
                with tf.train.MonitoredTrainingSession(master=server.target, is_chief=is_chief, config=sess_config,
                                                       checkpoint_dir="./target/tmp/input_output/" + str(
                                                           t)) as mon_sess:
                    # while not mon_sess.should_stop():
                    while True:
                        print (index, mon_sess.run([global_step_inc, w]))
                        sys.stdout.flush()
                        #time.sleep(1)
            except Exception as e:
                print('traceback.print_exc():')
                traceback.print_exc()
                sys.stdout.flush()
                raise e
            finally:
                SummaryWriterCache.clear()


if __name__ == "__main__":
    map_fun(context)
