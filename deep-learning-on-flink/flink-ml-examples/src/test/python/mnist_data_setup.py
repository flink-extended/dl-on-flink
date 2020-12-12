from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy
import tensorflow as tf
import math
import sys
from tensorflow.contrib.learn.python.learn.datasets import mnist


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def write_mnist_data(input_images, input_labels, output, partitions):
    with open(input_images, 'rb') as f:
        images = numpy.array(mnist.extract_images(f))

    with open(input_labels, 'rb') as f:
        labels = numpy.array(mnist.extract_labels(f, one_hot=True))

    shape = images.shape
    print("images.shape: {0}".format(shape))
    print("labels.shape: {0}".format(labels.shape))

    images = images.reshape(shape[0], shape[1], shape[2])
    num_per_part = int(math.ceil(float(shape[0]) / partitions))
    seq = 0
    filename = output + "/" + str(seq) + ".tfrecords"
    writer = tf.python_io.TFRecordWriter(filename)

    for i in range(shape[0]):
        if i != 0 and i % num_per_part == 0:
            writer.close()
            seq += 1
            filename = output + "/" + str(seq) + ".tfrecords"
            writer = tf.python_io.TFRecordWriter(filename)
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

    write_mnist_data(input + "/train-images-idx3-ubyte.gz",
                     input + "/train-labels-idx1-ubyte.gz",
                     output + "/train", int(partitions))

    write_mnist_data(input + "/t10k-images-idx3-ubyte.gz",
                     input + "/t10k-labels-idx1-ubyte.gz",
                     output + "/test", int(partitions))
