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
"""Utilities to dump and load Jsonable object to/from JSONs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import importlib
import inspect
import json
from typing import Any, Dict, List, Text, Type, Union
import logging
from six import with_metaclass

# This is the special key to indicate the serialized object type.
# Depending on which, the utility knows how to deserialize it back to its
# original type.
_AF_OBJECT_TYPE_KEY = '__af_object_type__'
_MODULE_KEY = '__module__'
_CLASS_KEY = '__class__'
_DATA = '__data__'

_BYTES_ENCODE = "ISO-8859-1"

RUNTIME_PARAMETER_PATTERN = (r'({\\*"__class__\\*": \\*"RuntimeParameter\\*", '
                             r'.*?})')


class _ObjectType(object):
    """Internal class to hold supported types."""
    # Indicates that the JSON dictionary is an instance of Jsonable type.
    # The dictionary has the states of the object and the object type info is
    # stored as __module__ and __class__ fields.
    JSONABLE = 'jsonable'
    # Indicates that the JSON dictionary is a python class.
    # The class info is stored as __module__ and __class__ fields in the
    # dictionary.
    CLASS = 'class'
    # Indicates that the JSON dictionary is an instance of a proto.Message
    # subclass. The class info of the proto python class is stored as __module__
    # and __class__ fields in the dictionary. The serialized value of the proto is
    # stored in the dictionary with key of _PROTO_VALUE_KEY.
    PROTO = 'proto'

    BYTES = 'bytes'

    SET = 'set'


class Jsonable(with_metaclass(abc.ABCMeta, object)):
    """Base class for serializing and deserializing objects to/from JSON.

    The default implementation assumes that the subclass can be restored by
    updating `self.__dict__` without invoking `self.__init__` function.. If the
    subclass cannot hold the assumption, it should
    override `to_json_dict` and `from_json_dict` to customize the implementation.
    """

    def to_json_dict(self) -> Dict[Text, Any]:
        """Convert from an object to a JSON serializable dictionary."""
        return self.__dict__

    @classmethod
    def from_json_dict(cls, dict_data: Dict[Text, Any]) -> Any:
        """Convert from dictionary data to an object."""
        instance = cls.__new__(cls)
        instance.__dict__ = dict_data
        return instance


JsonableValue = Union[bool, bytes, float, int, Jsonable, Text,
                      Type]
JsonableList = List[JsonableValue]
JsonableDict = Dict[Union[bytes, Text], Union[JsonableValue, JsonableList]]
JsonableType = Union[JsonableValue, JsonableList, JsonableDict]


class _DefaultEncoder(json.JSONEncoder):
    """Default JSON Encoder which encodes Jsonable object to JSON."""

    def encode(self, obj: Any) -> Text:
        try:
            """Override encode to prevent redundant dumping."""
            if obj.__class__.__name__ == 'RuntimeParameter' and obj.ptype == Text:
                return self.default(obj)

            return super(_DefaultEncoder, self).encode(obj)
        except Exception as e:
            logging.exception(obj.__class__.__name__)
            raise e

    def default(self, obj: Any) -> Any:
        # If obj is a str-typed RuntimeParameter, serialize it in place.
        if obj.__class__.__name__ == 'RuntimeParameter' and obj.ptype == Text:
            dict_data = {
                _AF_OBJECT_TYPE_KEY: _ObjectType.JSONABLE,
                _MODULE_KEY: obj.__class__.__module__,
                _CLASS_KEY: obj.__class__.__name__,
            }
            dict_data.update(obj.to_json_dict())
            return dumps(dict_data)

        if isinstance(obj, Jsonable):
            dict_data = {
                _AF_OBJECT_TYPE_KEY: _ObjectType.JSONABLE,
                _MODULE_KEY: obj.__class__.__module__,
                _CLASS_KEY: obj.__class__.__name__,
            }
            # Need to first check the existence of str-typed runtime parameter.
            data_patch = obj.to_json_dict()
            for k, v in data_patch.items():
                if v.__class__.__name__ == 'RuntimeParameter' and v.ptype == Text:
                    data_patch[k] = dumps(v)
            dict_data.update(data_patch)
            return dict_data

        if isinstance(obj, bytes):
            dict_data = {
                _AF_OBJECT_TYPE_KEY: _ObjectType.BYTES,
                _MODULE_KEY: obj.__class__.__module__,
                _CLASS_KEY: obj.__class__.__name__,
                _DATA: str(obj, _BYTES_ENCODE)
            }
            return dict_data

        if isinstance(obj, set):
            dict_data = {
                _AF_OBJECT_TYPE_KEY: _ObjectType.SET,
                _MODULE_KEY: obj.__class__.__module__,
                _CLASS_KEY: obj.__class__.__name__,
                _DATA: sorted(list(obj))
            }
            return dict_data

        if inspect.isclass(obj):
            return {
                _AF_OBJECT_TYPE_KEY: _ObjectType.CLASS,
                _MODULE_KEY: obj.__module__,
                _CLASS_KEY: obj.__name__,
            }

        return super(_DefaultEncoder, self).default(obj)


class _DefaultDecoder(json.JSONDecoder):
    """Default JSON Decoder which decodes JSON to Jsonable object."""

    def __init__(self, *args, **kwargs):
        super(_DefaultDecoder, self).__init__(
            object_hook=self._dict_to_object, *args, **kwargs)

    def _dict_to_object(self, dict_data: Dict[Text, Any]) -> Any:
        """Converts a dictionary to an object."""
        if _AF_OBJECT_TYPE_KEY not in dict_data:
            return dict_data

        object_type = dict_data.pop(_AF_OBJECT_TYPE_KEY)

        def _extract_class(d):
            module_name = d.pop(_MODULE_KEY)
            class_name = d.pop(_CLASS_KEY)
            return getattr(importlib.import_module(module_name), class_name)

        if object_type == _ObjectType.JSONABLE:
            jsonable_class_type = _extract_class(dict_data)
            if not issubclass(jsonable_class_type, Jsonable):
                raise ValueError('Class %s must be a subclass of Jsonable' %
                                 jsonable_class_type)
            return jsonable_class_type.from_json_dict(dict_data)

        if object_type == _ObjectType.CLASS:
            return _extract_class(dict_data)

        if object_type == _ObjectType.BYTES:
            return bytes(dict_data.pop(_DATA), _BYTES_ENCODE)

        if object_type == _ObjectType.SET:
            return set(dict_data.pop(_DATA))


def dumps(obj: Any) -> Text:
    """Dumps an object to JSON with Jsonable encoding."""
    return json.dumps(obj, cls=_DefaultEncoder, sort_keys=True)


def loads(s: Text) -> Any:
    """Loads a JSON into an object with Jsonable decoding."""
    return json.loads(s, cls=_DefaultDecoder)
