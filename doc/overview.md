# Deep Learning on Flink

Deep Learning on Flink aims to integrate Flink and deep learning frameworks
(e.g. TensorFlow, PyTorch, etc) to enable distributed deep learning training and
inference on a Flink cluster.

It runs the deep learning tasks inside a Flink operator so that Flink can help
establish a distributed environment, manage the resource, read/write the data
with the rich connectors in Flink and handle the failures.

Currently, Deep Learning on Flink supports TensorFlow.

# TensorFlow support
TensorFlow is a deep learning system developed by Google and open source,
which is widely used in the field of deep learning. There are many
inconveniences in distributed use and resource management of native TensorFlow,
but it can not integrate with the existing widely
used large data processing framework.

Flink is a data processing framework. It is widely used in data extraction,
feature preprocessing and data cleaning.

This project combines TensorFlow with Flink and provides users with more
convenient and useful tools.
**Currently, Flink job code can be written in both java with Flink Java API and
in python with PyFlink. The algorithm code is written in python.**

## Support Version
TensorFlow: 1.15.x & 2.3.x
Pytorch: 1.x
Flink: 1.14.x
