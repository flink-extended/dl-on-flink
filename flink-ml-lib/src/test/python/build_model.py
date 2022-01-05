# A quick fix to run TF 1.X code in TF 2.X, we may want to properly migrate the Python script to TF 2.X API.
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import os

a = tf.placeholder(tf.float32, shape=None, name="a")
b = tf.placeholder(tf.float32, shape=None, name="b")
e = tf.placeholder(tf.string, shape=None, name="e")
ee = tf.strings.to_number(
    e,
    out_type=tf.float32,
    name="ee"
)
v = tf.Variable(dtype=tf.float32, initial_value=tf.constant(1.0), name="v")
c = tf.add(a, b, name="c")
d = tf.add(c, v)
eee = tf.add(ee, v)
e4 = tf.as_string(eee)
global_step = tf.train.get_or_create_global_step()
global_step_inc = tf.assign_add(global_step, 1)
hooks = [tf.train.StopAtStepHook(last_step=2)]
with tf.Session() as mon_sess:
    mon_sess.run(tf.initialize_all_variables())
    for i in range(2):
        print(mon_sess.run([d, e4, global_step_inc], feed_dict={a: [1.0, 2.0, 3.0], b: [1.0, 2.0, 3.0],
                                                                e: ["1.0", "2.0", "3.0"]}))

    signatures = {
        tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: {
            'inputs': {'a': a, "b": b, "e": e},
            'outputs': {"d": d, "e4": e4},
            'method_name': tf.saved_model.signature_constants.PREDICT_METHOD_NAME
        }
    }

    export_dir = os.path.dirname(os.path.abspath(__file__)) + "../../../../target/test-classes/export2"
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
