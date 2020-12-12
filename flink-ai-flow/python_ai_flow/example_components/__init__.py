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
from python_ai_flow.local_python_job import register_local_example_component
from python_ai_flow.kubernetes_python_job import register_k8s_example_component
from python_ai_flow.example_components.pandas.example import PandasIOExample
from python_ai_flow.example_components.numpy.example import NumpyIOExample
from python_ai_flow.example_components.rabbitmq.example import RabbitMQExample
from python_ai_flow.example_components.user_function.example import UDFExampleComponent


register_local_example_component("pandas", PandasIOExample)
register_local_example_component("numpy", NumpyIOExample)
register_local_example_component("rabbitmq", RabbitMQExample)
register_local_example_component("udf", UDFExampleComponent)

register_k8s_example_component("pandas", PandasIOExample)
register_k8s_example_component("numpy", NumpyIOExample)
register_k8s_example_component("rabbitmq", RabbitMQExample)
register_k8s_example_component("udf", UDFExampleComponent)

