#!/usr/bin/env python

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

from __future__ import print_function
import os
import sys
import torch
import torch.distributed as dist
import json

""" All-Reduce example."""


def get_master_address(cluster_str):
    cluster_json = json.loads(cluster_str)
    worker_props = cluster_json['job'][0]['tasks']['0']['props']
    return worker_props['SYS:pytorch_master_ip'], worker_props['SYS:pytorch_master_port']


def map_func(context):
    print ('index:', context.index)
    print("context:", context)
    cluster_str = context.properties['cluster']
    master_ip, master_port = get_master_address(cluster_str)
    print('master:', master_ip, master_port)
    world_size = int(context.roleParallelism['worker'])
    distributed_flag = torch.distributed.is_available()
    print('distributed_flag:', distributed_flag)
    if distributed_flag:
        os.environ['MASTER_ADDR'] = master_ip
        os.environ['MASTER_PORT'] = master_port
        dist.init_process_group(dist.Backend.GLOO, rank=context.index, world_size=world_size)
        tensor = torch.ones(1)
        dist.all_reduce(tensor, op=dist.reduce_op.SUM)
        print('Rank ', context.index, ' has data ', tensor[0])
    sys.stdout.flush()
    print ("job num:", context.roleParallelism)
    print ("world size:", context.roleParallelism['worker'])
    sys.stdout.flush()
