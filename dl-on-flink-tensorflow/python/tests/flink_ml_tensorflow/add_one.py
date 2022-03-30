#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import tensorflow as tf

from dl_on_flink_tensorflow.tensorflow_context import TFContext

model_dir = "/tmp/model"


class ExportModelHook(tf.train.SessionRunHook):
    def __init__(self, model_export_path, input_tensor, output_tensor):
        self.model_export_path = model_export_path
        self.input_tensor = input_tensor
        self.output_tensor = output_tensor

    def end(self, session):
        g = session.graph
        g._unsafe_unfinalize()
        builder = tf.saved_model.builder.SavedModelBuilder(self.model_export_path)
        signature = tf.saved_model.predict_signature_def(inputs={"x": self.input_tensor},
                                                         outputs={"y": self.output_tensor})
        builder.add_meta_graph_and_variables(sess=session,
                                             tags=[tf.saved_model.tag_constants.SERVING],
                                             signature_def_map={
                                                 tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature},
                                             clear_devices=True,
                                             strip_default_attrs=True)
        builder.save()
        print("model export to {}".format(self.model_export_path))
        g.finalize()


def train(cluster_dict, job_name, task_index, export_model_path, dataset):
    print(cluster_dict, job_name, task_index, export_model_path)
    cluster = tf.train.ClusterSpec(cluster=cluster_dict)
    server = tf.train.Server(cluster, job_name=job_name, task_index=task_index)
    if job_name == "ps":
        server.join()
    elif job_name == "worker":
        with tf.device(tf.train.replica_device_setter(worker_device="/job:worker/task:{}".format(task_index),
                                                      cluster=cluster)):
            global_step = tf.train.get_or_create_global_step()
            dataset = dataset.map(lambda records: tf.decode_csv(records, [0.0]))
            x = dataset.make_one_shot_iterator().get_next()[0]
            y = tf.add(x, 1.0, "y")
            sess = tf.train.MonitoredTrainingSession(master=server.target, is_chief=task_index == 0,
                                                     checkpoint_dir=model_dir,
                                                     stop_grace_period_secs=10,
                                                     max_wait_secs=300,
                                                     chief_only_hooks=[ExportModelHook(export_model_path, x, y)])
            while not sess.should_stop():
                try:
                    print(sess.run([global_step, x, y]))
                except tf.errors.OutOfRangeError:
                    break

            sess.close()


def flink_stream_train(context):
    tf_context = TFContext(context)
    job_name = tf_context.get_node_type()
    index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster_config()
    export_model_path = tf_context.get_property("model_save_path")
    train(cluster_json, job_name, index, export_model_path, tf_context.get_tfdataset_from_flink())
