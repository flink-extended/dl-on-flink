## Flink AI Flow

Flink AI Flow is an open source framework that bridges big data and AI. It manages the entire machine learning project lifecycle as a unified workflow, including feature engineering, model training, model evaluation, model service, model inference, monitoring, etc. Throughout the entire workflow, Flink is used as the general purpose computing engine.

In addition to the capability of orchistrating a group of batch jobs, by leveraging an event-based scheduler, Flink AI Flow also supports workflows that contain streaming jobs. Such capability is quite useful for complicated real-time machine learning systems as well as other real-time workflows in general.

For more details, please check the [flink-ai-flow](flink-ai-flow) sub project.

## Deep Learning on Flink

Deep Learning on Flink aims to integrate Flink and deep learning framworks (e.g. TensorFlow, PyTorch, etc). It runs the deep learning tasks inside a Flink operator, so that Flink can help establish a distributed environment, manage the resource, read/write the records, and handle the failures.

Currently Deep Learning on Flink only supports TensorFlow.

For more details, please check the [deep-learning-on-flink](deep-learning-on-flink) sub project.
