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
"""
The ``aiflow.tensorflow`` module provides an API for loading tensorflow models.
"""
import warnings
from distutils.version import LooseVersion
import tensorflow
from ai_flow.endpoint.server.exception import AIFlowException


def _load_tensorflow_saved_model(model_uri, meta_graph_tags, signature_def_map_key, tf_session):
    """
    Load a specified TensorFlow model consisting of a TensorFlow metagraph and signature definition
    from a serialized TensorFlow ``SavedModel`` collection.

    :param model_uri: The local filesystem path or run-relative artifact path to the model.
    :param meta_graph_tags: A list of tags identifying the model's metagraph within the
                               serialized ``SavedModel`` object. For more information, see the
                               ``tags`` parameter of the `tf.saved_model.builder.SavedModelBuilder
                               method <https://www.tensorflow.org/api_docs/python/tf/saved_model/
                               builder/SavedModelBuilder#add_meta_graph>`_.
    :param signature_def_map_key: A string identifying the input/output signature associated with the
                                 model. This is a key within the serialized ``SavedModel``'s
                                 signature definition mapping. For more information, see the
                                 ``signature_def_map`` parameter of the
                                 ``tf.saved_model.builder.SavedModelBuilder`` method.
    :param tf_session: The TensorFlow session in which to load the metagraph.
                    Required in TensorFlow versions < 2.0.0. Unused in TensorFlow versions >= 2.0.0
    :return: For TensorFlow versions < 2.0.0:
             A TensorFlow signature definition of type:
             ``tensorflow.core.protobuf.meta_graph_pb2.SignatureDef``. This defines input and
             output tensors within the specified metagraph for inference.
             For TensorFlow versions >= 2.0.0:
             A callable graph (tensorflow.function) that takes inputs and returns inferences.
    """
    if LooseVersion(tensorflow.__version__) < LooseVersion('2.0.0'):
        loaded = tensorflow.saved_model.loader.load(
            sess=tf_session,
            tags=meta_graph_tags,
            export_dir=model_uri)
        loaded_sig = loaded.signature_def
    else:
        loaded = tensorflow.saved_model.load(  # pylint: disable=no-value-for-parameter
            tags=meta_graph_tags,
            export_dir=model_uri)
        loaded_sig = loaded.signatures
    if signature_def_map_key not in loaded_sig:
        raise AIFlowException("Could not find signature def key %s. Available keys are: %s"
                              % (signature_def_map_key, list(loaded_sig.keys())))
    return loaded_sig[signature_def_map_key]


def load_model(model_uri, meta_graph_tags, signature_def_map_key, tf_session=None):
    """
    Load a tensorflow model from a specific path.

    *With TensorFlow version <2.0.0, this method must be called within a TensorFlow graph context.*

    :param model_uri: The location, in URI format, of the tensorflow model. For example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``

    :param meta_graph_tags: A list of tags identifying the model's metagraph within the
                               serialized ``SavedModel`` object. For more information, see the
                               ``tags`` parameter of the `tf.saved_model.builder.SavedModelBuilder
                               method <https://www.tensorflow.org/api_docs/python/tf/saved_model/
                               builder/SavedModelBuilder#add_meta_graph>`_.

    :param signature_def_map_key: A string identifying the input/output signature associated with the
                                 model. This is a key within the serialized ``SavedModel``'s
                                 signature definition mapping. For more information, see the
                                 ``signature_def_map`` parameter of the
                                 ``tf.saved_model.builder.SavedModelBuilder`` method.

    :param tf_session: The TensorFlow session in which to load the model. If using TensorFlow
                    version >= 2.0.0, this argument is ignored. If using TensorFlow <2.0.0, if no
                    session is passed to this function, aiflow will attempt to load the model using
                    the default TensorFlow session.  If no default session is available, then the
                    function raises an exception.
    :return: For TensorFlow < 2.0.0, a TensorFlow signature definition of type:
             ``tensorflow.core.protobuf.meta_graph_pb2.SignatureDef``. This defines the input and
             output tensors for model inference.
             For TensorFlow >= 2.0.0, A callable graph (tf.function) that takes inputs and
             returns inferences.
    """
    if LooseVersion(tensorflow.__version__) < LooseVersion('2.0.0'):
        if not tf_session:
            tf_session = tensorflow.get_default_session()
            if not tf_session:
                raise AIFlowException("No TensorFlow session found while calling load_model()." +
                                      "You can set the default Tensorflow session before calling" +
                                      " load_model via `session.as_default()`, or directly pass " +
                                      "a session in which to load the model via the tf_sess " +
                                      "argument.")

    else:
        if tf_session:
            warnings.warn("A TensorFlow session was passed into load_model, but the " +
                          "currently used version is TF 2.0 where sessions are deprecated. " +
                          "The tf_sess argument will be ignored.", FutureWarning)
    return _load_tensorflow_saved_model(model_uri=model_uri,
                                        meta_graph_tags=meta_graph_tags,
                                        signature_def_map_key=signature_def_map_key,
                                        tf_session=tf_session)
