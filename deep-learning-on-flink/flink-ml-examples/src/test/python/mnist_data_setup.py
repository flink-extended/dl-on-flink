from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy
import tensorflow as tf
import math
import sys
from tensorflow.keras.datasets import mnist


# from tensorflow.contrib.learn.python.learn.datasets import mnist

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def write_mnist_data(images, labels, output, partitions):
    shape = images.shape
    print("images.shape: {0}".format(shape))
    print("labels.shape: {0}".format(labels.shape))

    images = images.reshape(shape[0], shape[1], shape[2])
    num_per_part = int(math.ceil(float(shape[0]) / partitions))
    seq = 0
    filename = output + "/" + str(seq) + ".tfrecords"
    writer = tf.io.TFRecordWriter(filename)

    for i in range(shape[0]):
        if i != 0 and i % num_per_part == 0:
            writer.close()
            seq += 1
            filename = output + "/" + str(seq) + ".tfrecords"
            writer = tf.io.TFRecordWriter(filename)
        image_raw = images[i].tostring()
        example = tf.train.Example(features=tf.train.Features(feature={
            'image_raw': _bytes_feature(image_raw),
            'label': _int64_feature(labels[i].astype(int))
        }))
        writer.write(example.SerializeToString())
    writer.close()


if __name__ == "__main__":

    if 'args' in globals():
        global args
        input = args.get("input")
        output = args.get("output")
        partitions = args.get("partitions")
    else:
        assert len(sys.argv) == 4, 'Invalid cmd line argument ' + str(sys.argv)
        input = sys.argv[1]
        output = sys.argv[2]
        partitions = sys.argv[3]

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    write_mnist_data(x_train, tf.keras.utils.to_categorical(y_train), output + "/train", int(partitions))

    write_mnist_data(x_test, tf.keras.utils.to_categorical(y_test), output + "/test", int(partitions))
