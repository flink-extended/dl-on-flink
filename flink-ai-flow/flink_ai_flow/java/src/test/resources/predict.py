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
import tensorflow as tf
import os


a = tf.placeholder(tf.int32, shape=None, name="a")
b = tf.placeholder(tf.int32, shape=None, name="b")
c = tf.placeholder(tf.int32, shape=None, name="c")

v = tf.Variable(dtype=tf.int32, initial_value=tf.constant(2), name="v")
aa = tf.multiply(a, v)
bb = tf.multiply(a, v)
cc = tf.add(c, bb)
global_step = tf.contrib.framework.get_or_create_global_step()
global_step_inc = tf.assign_add(global_step, 1)
hooks = [tf.train.StopAtStepHook(last_step=2)]
with tf.Session() as mon_sess:
    mon_sess.run(tf.initialize_all_variables())
    for i in range(2):
        print(mon_sess.run([aa, cc, global_step_inc], feed_dict={a: [1, 2, 3], b: [1, 2, 3],
                                                                 c: [1, 2, 3]}))

    signatures = {
        tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: {
            'inputs': {'a': a, "b": b, "c": c},
            'outputs': {"aa": aa, "cc": cc},
            'method_name': tf.saved_model.signature_constants.PREDICT_METHOD_NAME
        }
    }

    export_dir = os.path.dirname(os.path.abspath(__file__)) + "/export2"
    try:
        tf.gfile.DeleteRecursively(export_dir)
    except tf.errors.OpError:
        pass
    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)

    signature_def_map = {}
    for key, sig in signatures.items():
        signature_def_map[key] = tf.saved_model.signature_def_utils.build_signature_def(
            inputs={name: tf.saved_model.utils.build_tensor_info(tensor) for name, tensor in
                    sig['inputs'].items()},
            outputs={name: tf.saved_model.utils.build_tensor_info(tensor) for name, tensor in
                     sig['outputs'].items()},
            method_name=sig['method_name'] if 'method_name' in sig else key)

        builder.add_meta_graph_and_variables(
            mon_sess,
            tf.saved_model.tag_constants.SERVING.split(','),
            signature_def_map=signature_def_map,
            clear_devices=True)
        builder.save()
