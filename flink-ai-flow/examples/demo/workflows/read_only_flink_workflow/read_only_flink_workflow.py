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
import ai_flow as af
from ai_flow_plugins.job_plugins.flink.read_only_flink import ReadOnlyFlinkProcessor


def main():
    af.init_ai_flow_context()

    with af.job_config("read_only_flink_job"):
        af.user_define_operation(processor=ReadOnlyFlinkProcessor())

    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)


if __name__ == '__main__':
    main()
