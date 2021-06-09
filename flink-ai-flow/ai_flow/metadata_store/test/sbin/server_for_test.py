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
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../../../..")))

from ai_flow.endpoint.server.server import AIFlowServer

if __name__ == '__main__':
    fd, temp_dbfile = tempfile.mkstemp()
    os.close(fd)
    db_uri = '%s%s' % ('sqlite:///', temp_dbfile)
    server = AIFlowServer(store_uri=db_uri)
    server.run(is_block=True)
