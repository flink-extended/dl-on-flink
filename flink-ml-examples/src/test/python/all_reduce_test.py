#!/usr/bin/env python
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
