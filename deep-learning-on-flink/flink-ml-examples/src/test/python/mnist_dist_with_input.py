# Distributed MNIST on grid based on TensorFlow MNIST example

from datetime import datetime
# A quick fix to run TF 1.X code in TF 2.X, we may want to properly migrate the Python script to TF 2.X API.
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.python.summary.writer.writer_cache import FileWriterCache as SummaryWriterCache
import math
import numpy
import json
import sys
from flink_ml_tensorflow.tensorflow_context import TFContext


def export_saved_model(sess, export_dir, tag_set, signatures):
    g = sess.graph
    g._unsafe_unfinalize()
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
            sess,
            tag_set.split(','),
            signature_def_map=signature_def_map,
            clear_devices=True)

        g.finalize()
        builder.save()


class ExportHook(tf.train.SessionRunHook):
    def __init__(self, export_dir, input_tensor, output_tensor):
        self.export_dir = export_dir
        self.input_tensor = input_tensor
        self.output_tensor = output_tensor

    def end(self, session):
        print("{} ======= Exporting to: {}".format(datetime.now().isoformat(), self.export_dir))
        signatures = {
            tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: {
                'inputs': {'image': self.input_tensor},
                'outputs': {'prediction': self.output_tensor},
                'method_name': tf.saved_model.signature_constants.PREDICT_METHOD_NAME
            }
        }
        export_saved_model(session, self.export_dir, tf.saved_model.tag_constants.SERVING,
                           signatures)
        print("{} ======= Done exporting".format(datetime.now().isoformat()))


def decode(features):
    image = tf.decode_raw(features['image_raw'], tf.uint8)
    label = tf.one_hot(features['label'], 10, on_value=1)
    return image, label


def input_iter(context, batch_size):
    features = {'label': tf.FixedLenFeature([], tf.int64), 'image_raw': tf.FixedLenFeature([], tf.string)}
    dataset = context.flink_stream_dataset()
    dataset = dataset.map(lambda record: tf.parse_single_example(record, features=features))
    dataset = dataset.map(decode)
    dataset = dataset.batch(batch_size)
    iterator = tf.data.make_one_shot_iterator(dataset)
    return iterator


def map_fun(context):
    tf_context = TFContext(context)
    job_name = tf_context.get_role_name()
    task_index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster()
    print (cluster_json)
    sys.stdout.flush()

    props = context.properties
    batch_size = int(props.get("batch_size"))
    checkpoint_dir = props.get("checkpoint_dir")
    export_dir = props.get("export_dir")

    # Parameters
    IMAGE_PIXELS = 28
    hidden_units = 128

    cluster = tf.train.ClusterSpec(cluster=cluster_json)
    server = tf.train.Server(cluster, job_name=job_name, task_index=task_index)

    def feed_dict(images, labels):
        xs = numpy.array(images)
        xs = xs.astype(numpy.float32)
        xs = xs / 255.0
        ys = numpy.array(labels)
        ys = ys.astype(numpy.uint8)
        return (xs, ys)

    if job_name == "ps":
        from time import sleep
        while True:
            sleep(1)
    elif job_name == "worker":

        # Assigns ops to the local worker by default.
        with tf.device(
                tf.train.replica_device_setter(worker_device="/job:worker/task:" + str(task_index), cluster=cluster)):

            # Placeholders or QueueRunner/Readers for input data
            x = tf.placeholder(tf.float32, [None, IMAGE_PIXELS * IMAGE_PIXELS], name="x")
            y_ = tf.placeholder(tf.float32, [None, 10], name="y_")

            # Variables of the hidden layer
            hid_w = tf.Variable(
                tf.truncated_normal([IMAGE_PIXELS * IMAGE_PIXELS, hidden_units], stddev=1.0 / IMAGE_PIXELS),
                name="hid_w")
            hid_b = tf.Variable(tf.zeros([hidden_units]), name="hid_b")
            hid_lin = tf.nn.xw_plus_b(x, hid_w, hid_b)
            hid = tf.nn.relu(hid_lin)

            # Variables of the softmax layer
            sm_w = tf.Variable(
                tf.truncated_normal([hidden_units, 10], stddev=1.0 / math.sqrt(hidden_units)),
                name="sm_w")
            sm_b = tf.Variable(tf.zeros([10]), name="sm_b")
            y = tf.nn.softmax(tf.nn.xw_plus_b(hid, sm_w, sm_b))

            global_step = tf.train.get_or_create_global_step()

            loss = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y, 1e-10, 1.0)))

            train_op = tf.train.AdagradOptimizer(0.01).minimize(loss, global_step=global_step)

            # Test trained model
            label = tf.argmax(y_, 1, name="label")
            prediction = tf.argmax(y, 1, name="prediction")
            correct_prediction = tf.equal(prediction, label)

            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="accuracy")

            iter = input_iter(tf_context, batch_size)
            next_batch = iter.get_next()

            is_chief = (task_index == 0)
            sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False,
                                         device_filters=["/job:ps", "/job:worker/task:%d" % task_index])

            # The MonitoredTrainingSession takes care of session initialization, restoring from
            #  a checkpoint, and closing when done or an error occurs
            mon_sess = tf.train.MonitoredTrainingSession(master=server.target, is_chief=is_chief,
                                                         checkpoint_dir=checkpoint_dir,
                                                         stop_grace_period_secs=10, max_wait_secs=300,
                                                         config=sess_config,
                                                         chief_only_hooks=[ExportHook(export_dir, x,
                                                                                      prediction)])
            processed = 0
            while not mon_sess.should_stop():
                # Run a training step asynchronously
                # See `tf.train.SyncReplicasOptimizer` for additional details on how to
                # perform *synchronous* training.
                try:
                    images, labels = mon_sess.run(next_batch)
                    processed += images.shape[0]
                    # print mon_sess.run(next_batch)
                except tf.errors.OutOfRangeError:
                    break

                batch_xs, batch_ys = feed_dict(images, labels)
                feed = {x: batch_xs, y_: batch_ys}

                if len(batch_xs) > 0 and not mon_sess.should_stop():
                    _, step = mon_sess.run([train_op, global_step], feed_dict=feed)
                    if step % 100 == 0:
                        print("{0}, Task {1} step: {2} accuracy: {3}".format(
                            datetime.now().isoformat(), task_index, step,
                            mon_sess.run(accuracy, {x: batch_xs, y_: batch_ys})))
                        sys.stdout.flush()

            print(str(processed) + " records processed.")
            print("{0} stopping MonitoredTrainingSession".format(datetime.now().isoformat()))
            mon_sess.close()

    SummaryWriterCache.clear()


if __name__ == "__main__":
    map_fun(context)
