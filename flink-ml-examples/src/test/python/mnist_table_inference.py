# Distributed MNIST on grid based on TensorFlow MNIST example

from __future__ import print_function
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


def test_log(message):
    print(message)
    sys.stdout.flush()


def decode(features):
    image = tf.decode_raw(features['image_raw'], tf.uint8)
    label = tf.one_hot(features['label'], 10, on_value=1)
    return image, label


def feed_dict(images, labels):
    xs = numpy.array(images)
    xs = xs.astype(numpy.float32)
    xs = xs / 255.0
    ys = numpy.array(labels)
    ys = ys.astype(numpy.uint8)
    return (xs, ys)


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
    epochs = int(props.get("epochs"))
    checkpoint_dir = props.get("checkpoint_dir")
    export_dir = props.get("export_dir")

    # Parameters
    IMAGE_PIXELS = 28
    hidden_units = 128

    session = tf.Session()
    signature_key = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
    input_key = 'image'
    output_key = 'prediction'
    # saved_model_dir = '/home/chen/code/TensorFlowOnFlink/target/export/1539071075170/'
    test_log("before load")
    meta_graph_def = tf.saved_model.loader.load(session, [tf.saved_model.tag_constants.SERVING], export_dir=export_dir)
    test_log("after load")
    signature = meta_graph_def.signature_def

    x_tensor_name = signature[signature_key].inputs[input_key].name
    test_log(x_tensor_name)
    y_tensor_name = signature[signature_key].outputs[output_key].name
    test_log(y_tensor_name)
    x = session.graph.get_tensor_by_name(x_tensor_name)
    y = session.graph.get_tensor_by_name(y_tensor_name)

    # write_feed, write_op, close_op = context.getOutputWriterOp()
    write_feed = tf.placeholder(dtype=tf.string)
    write_op, close_op = tf_context.output_writer_op([write_feed])
    iter = input_iter(tf_context, batch_size)
    next_batch = iter.get_next()
    prediction = tf.argmax(next_batch[1], 1, name="prediction")

    while True:
        try:
            images, labels, labels_ = session.run([next_batch[0], next_batch[1], prediction])
        except tf.errors.OutOfRangeError:
            break
        batch_xs, batch_ys = feed_dict(images, labels)
        feed = {x: batch_xs}
        # test_log(feed_data)
        # input_res = session.run(x_, feed_dict={input_data: feed_data})
        # print "input_data", input_res
        y_res = session.run(y, feed_dict=feed)
        # print "y_res", y_res, "y_org", labels_
        # sys.stdout.flush()
        for i in range(len(y_res)):
            example = tf.train.Example(features=tf.train.Features(
                feature={
                    'predict_label': tf.train.Feature(int64_list=tf.train.Int64List(value=[y_res[i]])),
                    'label_org': tf.train.Feature(int64_list=tf.train.Int64List(value=[labels_[i]])),
                }))
            # print "write:", i
            sys.stdout.flush()
            session.run(write_op, feed_dict={write_feed: example.SerializeToString()})

    session.run(close_op)

    SummaryWriterCache.clear()


if __name__ == "__main__":
    map_fun(context)
