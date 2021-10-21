# Flink AI Extended

Flink AI Extended is a project extending Flink to various machine learning scenarios.
Currently it contains the following two subprojects.

## Flink AI Flow
 
### Note: Flink AI Flow has moved to https://github.com/flink-extended/ai-flow

Flink AI Flow is an open source framework that bridges big data and AI. 
It manages the entire machine learning project lifecycle as a unified workflow, including feature engineering, 
model training, model evaluation, model service, model inference, monitoring, etc. 
Throughout the entire workflow, Flink is used as the general purpose computing engine.

In addition to the capability of orchestrating a group of batch jobs, 
by leveraging an event-based scheduler(enhanced version of Airflow), 
Flink AI Flow also supports workflows that contain streaming jobs. Such capability is quite useful for complicated 
real-time machine learning systems as well as other real-time workflows in general.

## Deep Learning on Flink

Deep Learning on Flink aims to integrate Flink and deep learning frameworks (e.g. TensorFlow, PyTorch, etc).
It runs the deep learning tasks inside a Flink operator, so that Flink can help establish a distributed environment, 
manage the resource, read/write the records and handle the failures.

For more details, please check the [deep-learning-on-flink](deep-learning-on-flink) sub project.

## Contact Us

For more information, you can join the **Flink AI Flow Users Group** on [DingTalk](https://www.dingtalk.com) to contact us.
The number of the DingTalk group is `35876083`. 

You can also join the group by scanning the QR code below:

![](flink-ai-flow/doc/images/dingtalk_qr_code.png)
