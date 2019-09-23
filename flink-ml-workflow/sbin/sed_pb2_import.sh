#!/usr/bin/env bash
cd ../python/flink_ml_workflow/proto
#sed -i -E 's/^\(import.*_pb2\)/from \. \1/' *pb2*.py
sed -i -E 's/^import meta_data_pb2 as meta__data__pb2/from \. import meta_data_pb2 as meta__data__pb2/' *pb2*.py
rm -rf *.py-E
