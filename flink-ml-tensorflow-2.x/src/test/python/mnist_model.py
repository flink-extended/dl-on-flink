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
from sys import argv

import numpy as np
import tensorflow as tf

print("TensorFlow version:", tf.__version__)

if len(argv) == 2:
    save_path = argv[1]
else:
    save_path = "/tmp/model"


class ArgmaxLayer(tf.keras.layers.Layer):
    def call(self, inputs, **kwargs):
        return tf.cast(tf.argmax(inputs), tf.float32)


model = tf.keras.models.Sequential([
    tf.keras.layers.InputLayer(input_shape=(784,)),
    tf.keras.layers.Dense(units=10),
    ArgmaxLayer()
])
loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer='adam',
              loss=loss)
x_train = np.array([[1.0] * 784])
model(x_train)


@tf.function(input_signature=[tf.TensorSpec((784, None), name="image")])
def predict(image):
    return {"prediction": model(image)}


model.save(save_path, save_format='tf', signatures={
    tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY: predict})
