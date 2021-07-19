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

docs=$(dirname "${BASH_SOURCE[0]}")
docs=$(cd "docs"; pwd)
workdir=$docs
tmpdir="$workdir"/__tmp
cd "$workdir"
[ -e "$workdir"/source_rst ] && rm -r "$workdir"/source_rst/
mkdir "$workdir"/source_rst/
mkdir "$tmpdir"
sphinx-apidoc -f -M -o "$tmpdir"/ "$workdir"/../ai_flow "$workdir"/../ai_flow/*test*
cp -a "$tmpdir"/. "$workdir"/source_rst/
rm "$tmpdir"/*
sphinx-apidoc -f -M -o "$tmpdir"/ "$workdir"/../ai_flow_plugins "$workdir"/../ai_flow_plugins/*test*
cp -a "$tmpdir"/. "$workdir"/source_rst/
rm -r "$tmpdir"
make clean html