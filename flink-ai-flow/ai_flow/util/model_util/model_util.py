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
import os
import tempfile
import uuid
import zipfile
import oss2
import warnings
import tensorflow
import pickle

from distutils.version import LooseVersion
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Text, Dict

from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.util.file_util.zip_file_util import make_dir_zipfile, make_file_zipfile


class ModelManager(ABC):

    @abstractmethod
    def download_model(self, remote_path, local_path=None):
        pass

    @abstractmethod
    def save_model(self, local_path, remote_path=None):
        pass


class OSSModelManager(ModelManager):

    def __init__(self, config: Dict[Text, Text]):
        ack_id = config.get('blob_server.access_key_id', None)
        ack_secret = config.get('blob_server.access_key_secret', None)
        endpoint = config.get('blob_server.endpoint', None)
        bucket_name = config.get('blob_server.bucket', None)
        auth = oss2.Auth(ack_id, ack_secret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def download_model(self, remote_path, local_path=None):
        """
        download an uploaded model in Aliyun OSS.
        :param remote_path: the object key of the file in oss.
        :param local_path: the user specified local path of the downloaded file. the local_path must be a directory
        :return: the downloaded file path.
        """
        if local_path is not None:
            local_file_dir = local_path
        else:
            local_file_dir = 'tmp_model-' + str(uuid.uuid1())
        tmp_dir = Path(tempfile.gettempdir())
        tmp_zip_file = str(tmp_dir / local_file_dir) + '.zip'
        oss_object_key = remote_path
        self.bucket.get_object_to_file(key=oss_object_key, filename=tmp_zip_file)
        with zipfile.ZipFile(tmp_zip_file, 'r') as zip_ref:
            top_name = zip_ref.namelist()[0]
            extract_path = str(tmp_dir / local_file_dir)
            zip_ref.extractall(extract_path)
        downloaded_local_path = Path(extract_path) / top_name
        return str(downloaded_local_path)

    def save_model(self, local_path, remote_path=None) -> Text:
        """
        save a local export model to remote storage(Aliyun OSS)
        :param local_path: the local path of the model, the oss storage only supports binary files, thus we have to
        make the local path file a zip.
        :param remote_path: the object_key of the uploaded file in oss with the pattern like abc/efg/123.jpg
        :return: the object_key of uploaded file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(local_path)
            zip_file_name = os.path.splitext(local_path.name)[0] + '.zip'
            temp_dir_path = Path(temp_dir)
            zip_file_path = temp_dir_path / zip_file_name
            if local_path.is_dir():
                make_dir_zipfile(str(local_path), zip_file_path)
            else:
                make_file_zipfile(str(local_path), zip_file_path)
            if remote_path is None:
                object_key = 'ai-flow-model-manager/' + zip_file_name
            else:
                object_key = remote_path
            self.bucket.put_object_from_file(key=object_key, filename=str(zip_file_path))
        return object_key


def _load_model_from_local_file(path):
    """Load a scikit-learn model saved as an aiflow artifact on the local file system."""
    with open(path, "rb") as f:
        return pickle.load(f)


def load_scikit_learn_model(model_uri):
    """
    Load a scikit-learn model from a local file.

    :param model_uri: The location, in URI format, of the aiflow model, for example:

                      - ``/Users/aiflow/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``

    :return: A scikit-learn model.
    """
    return _load_model_from_local_file(path=model_uri)


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


def load_tensorflow_saved_model(model_uri, meta_graph_tags, signature_def_map_key, tf_session=None):
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
