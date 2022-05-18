#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import glob
import os

from pyflink.util.java_utils import add_jars_to_context_class_loader


def find_jar_path():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                              "target")
    jar_name = "dl-on-flink-tensorflow-*-jar-with-dependencies.jar"
    paths = glob.glob(os.path.join(target_dir, jar_name))
    if len(paths) < 1:
        raise RuntimeError(
            "Cannot find dl-on-flink-tensorflow jar, "
            "please make sure you have run `mvn package`")
    elif len(paths) >= 2:
        raise RuntimeError(
            "Found more than one dl-on-flink-tensorflow jar {}".format(paths))
    return paths[0]


def add_dl_on_flink_jar():
    add_jars_to_context_class_loader(["file://{}".format(find_jar_path())])


def get_resource_folder():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "src",
                     "test", "resources"))
