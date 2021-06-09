# Codegen 

The Codegen will show you how to install GRPC related dependencies and help you codegen GRPC related code.

## Require

1. python3.7
2. pip
3. go1.14
4. grpc

## Install 

```shell
# install protobuf
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.15.6/protobuf-all-3.15.6.tar.gz
tar -zxvf protobuf-all-3.15.6.tar.gz
cd protobuf-3.15.6
./configure
make
make check
make install

# install google-api-core
pip install google-api-core==1.26.1

# install grpcio
pip install grpcio==1.34.0
pip install grpcio-tools==1.34.0
```

# Codegen

```shell
sh gen_protobuf.sh
```
