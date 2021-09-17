#!/usr/bin/env bash
##
## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##
set -e

current_dir=$(cd "$(dirname "$0")";pwd)
java_dir=${current_dir}/../../java/src/main/java/org/aiflow/notification/proto
go_dir=${current_dir}/../go/notification_service
# Add licenses to generated python files
for i in ${current_dir}/*.py
do
   if ! [[ $i == *"__init__"* ]]; then
     sed -i '' -e '1i \
#\
# Licensed to the Apache Software Foundation (ASF) under one\
# or more contributor license agreements.  See the NOTICE file\
# distributed with this work for additional information\
# regarding copyright ownership.  The ASF licenses this file\
# to you under the Apache License, Version 2.0 (the\
# "License"); you may not use this file except in compliance\
# with the License.  You may obtain a copy of the License at\
#\
#   http://www.apache.org/licenses/LICENSE-2.0\
#\
# Unless required by applicable law or agreed to in writing,\
# software distributed under the License is distributed on an\
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY\
# KIND, either express or implied.  See the License for the\
# specific language governing permissions and limitations\
# under the License.\
#\
\
' $i
   fi

done

# Add licenses to generated java files
for i in ${java_dir}/*.java
do
   sed -i '' -e '1i \
/*\
\ * Licensed to the Apache Software Foundation (ASF) under one\
\ * or more contributor license agreements.  See the NOTICE file\
\ * distributed with this work for additional information\
\ * regarding copyright ownership.  The ASF licenses this file\
\ * to you under the Apache License, Version 2.0 (the\
\ * "License"); you may not use this file except in compliance\
\ * with the License.  You may obtain a copy of the License at\
\ *\
\ *   http://www.apache.org/licenses/LICENSE-2.0\
\ *\
\ * Unless required by applicable law or agreed to in writing,\
\ * software distributed under the License is distributed on an\
\ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY\
\ * KIND, either express or implied.  See the License for the\
\ * specific language governing permissions and limitations\
\ * under the License.\
\ */\
' $i
done


# Add licenses to generated go files
for i in ${go_dir}/*.gw.go
do
   sed -i '' -e '1i \
//\
// Licensed to the Apache Software Foundation (ASF) under one\
// or more contributor license agreements.  See the NOTICE file\
// distributed with this work for additional information\
// regarding copyright ownership.  The ASF licenses this file\
// to you under the Apache License, Version 2.0 (the\
// "License"); you may not use this file except in compliance\
// with the License.  You may obtain a copy of the License at\
//\
//     http://www.apache.org/licenses/LICENSE-2.0\
//\
// Unless required by applicable law or agreed to in writing, software\
// distributed under the License is distributed on an "AS IS" BASIS,\
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\
// See the License for the specific language governing permissions and\
// limitations under the License.\
\
' $i
done


