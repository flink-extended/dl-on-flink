/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.aiflow.proto;

import static io.grpc.MethodDescriptor.generateFullMethodName;
import static io.grpc.stub.ClientCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ClientCalls.asyncClientStreamingCall;
import static io.grpc.stub.ClientCalls.asyncServerStreamingCall;
import static io.grpc.stub.ClientCalls.asyncUnaryCall;
import static io.grpc.stub.ClientCalls.blockingServerStreamingCall;
import static io.grpc.stub.ClientCalls.blockingUnaryCall;
import static io.grpc.stub.ClientCalls.futureUnaryCall;
import static io.grpc.stub.ServerCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ServerCalls.asyncClientStreamingCall;
import static io.grpc.stub.ServerCalls.asyncServerStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnaryCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.29.0-SNAPSHOT)",
    comments = "Source: metadata_service.proto")
public final class MetadataServiceGrpc {

  private MetadataServiceGrpc() {}

  public static final String SERVICE_NAME = "ai_flow.MetadataService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetDatasetByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getDatasetById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetDatasetByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetDatasetByIdMethod;
    if ((getGetDatasetByIdMethod = MetadataServiceGrpc.getGetDatasetByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetDatasetByIdMethod = MetadataServiceGrpc.getGetDatasetByIdMethod) == null) {
          MetadataServiceGrpc.getGetDatasetByIdMethod = getGetDatasetByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getDatasetById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getDatasetById"))
              .build();
        }
      }
    }
    return getGetDatasetByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetDatasetByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getDatasetByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetDatasetByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetDatasetByNameMethod;
    if ((getGetDatasetByNameMethod = MetadataServiceGrpc.getGetDatasetByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetDatasetByNameMethod = MetadataServiceGrpc.getGetDatasetByNameMethod) == null) {
          MetadataServiceGrpc.getGetDatasetByNameMethod = getGetDatasetByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getDatasetByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getDatasetByName"))
              .build();
        }
      }
    }
    return getGetDatasetByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListDatasetsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listDatasets",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListDatasetsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListDatasetsMethod;
    if ((getListDatasetsMethod = MetadataServiceGrpc.getListDatasetsMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListDatasetsMethod = MetadataServiceGrpc.getListDatasetsMethod) == null) {
          MetadataServiceGrpc.getListDatasetsMethod = getListDatasetsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listDatasets"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listDatasets"))
              .build();
        }
      }
    }
    return getListDatasetsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerDataset",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest, com.aiflow.proto.Message.Response> getRegisterDatasetMethod;
    if ((getRegisterDatasetMethod = MetadataServiceGrpc.getRegisterDatasetMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterDatasetMethod = MetadataServiceGrpc.getRegisterDatasetMethod) == null) {
          MetadataServiceGrpc.getRegisterDatasetMethod = getRegisterDatasetMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerDataset"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerDataset"))
              .build();
        }
      }
    }
    return getRegisterDatasetMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetWithCatalogMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerDatasetWithCatalog",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetWithCatalogMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest, com.aiflow.proto.Message.Response> getRegisterDatasetWithCatalogMethod;
    if ((getRegisterDatasetWithCatalogMethod = MetadataServiceGrpc.getRegisterDatasetWithCatalogMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterDatasetWithCatalogMethod = MetadataServiceGrpc.getRegisterDatasetWithCatalogMethod) == null) {
          MetadataServiceGrpc.getRegisterDatasetWithCatalogMethod = getRegisterDatasetWithCatalogMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerDatasetWithCatalog"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerDatasetWithCatalog"))
              .build();
        }
      }
    }
    return getRegisterDatasetWithCatalogMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerDatasets",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest,
      com.aiflow.proto.Message.Response> getRegisterDatasetsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest, com.aiflow.proto.Message.Response> getRegisterDatasetsMethod;
    if ((getRegisterDatasetsMethod = MetadataServiceGrpc.getRegisterDatasetsMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterDatasetsMethod = MetadataServiceGrpc.getRegisterDatasetsMethod) == null) {
          MetadataServiceGrpc.getRegisterDatasetsMethod = getRegisterDatasetsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerDatasets"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerDatasets"))
              .build();
        }
      }
    }
    return getRegisterDatasetsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest,
      com.aiflow.proto.Message.Response> getUpdateDatasetMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateDataset",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest,
      com.aiflow.proto.Message.Response> getUpdateDatasetMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest, com.aiflow.proto.Message.Response> getUpdateDatasetMethod;
    if ((getUpdateDatasetMethod = MetadataServiceGrpc.getUpdateDatasetMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateDatasetMethod = MetadataServiceGrpc.getUpdateDatasetMethod) == null) {
          MetadataServiceGrpc.getUpdateDatasetMethod = getUpdateDatasetMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateDataset"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateDataset"))
              .build();
        }
      }
    }
    return getUpdateDatasetMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteDatasetByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteDatasetById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteDatasetByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteDatasetByIdMethod;
    if ((getDeleteDatasetByIdMethod = MetadataServiceGrpc.getDeleteDatasetByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteDatasetByIdMethod = MetadataServiceGrpc.getDeleteDatasetByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteDatasetByIdMethod = getDeleteDatasetByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteDatasetById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteDatasetById"))
              .build();
        }
      }
    }
    return getDeleteDatasetByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteDatasetByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteDatasetByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteDatasetByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteDatasetByNameMethod;
    if ((getDeleteDatasetByNameMethod = MetadataServiceGrpc.getDeleteDatasetByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteDatasetByNameMethod = MetadataServiceGrpc.getDeleteDatasetByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteDatasetByNameMethod = getDeleteDatasetByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteDatasetByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteDatasetByName"))
              .build();
        }
      }
    }
    return getDeleteDatasetByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetModelRelationByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelRelationById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetModelRelationByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetModelRelationByIdMethod;
    if ((getGetModelRelationByIdMethod = MetadataServiceGrpc.getGetModelRelationByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelRelationByIdMethod = MetadataServiceGrpc.getGetModelRelationByIdMethod) == null) {
          MetadataServiceGrpc.getGetModelRelationByIdMethod = getGetModelRelationByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelRelationById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelRelationById"))
              .build();
        }
      }
    }
    return getGetModelRelationByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetModelRelationByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelRelationByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetModelRelationByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetModelRelationByNameMethod;
    if ((getGetModelRelationByNameMethod = MetadataServiceGrpc.getGetModelRelationByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelRelationByNameMethod = MetadataServiceGrpc.getGetModelRelationByNameMethod) == null) {
          MetadataServiceGrpc.getGetModelRelationByNameMethod = getGetModelRelationByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelRelationByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelRelationByName"))
              .build();
        }
      }
    }
    return getGetModelRelationByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListModelRelationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listModelRelation",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListModelRelationMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListModelRelationMethod;
    if ((getListModelRelationMethod = MetadataServiceGrpc.getListModelRelationMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListModelRelationMethod = MetadataServiceGrpc.getListModelRelationMethod) == null) {
          MetadataServiceGrpc.getListModelRelationMethod = getListModelRelationMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listModelRelation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listModelRelation"))
              .build();
        }
      }
    }
    return getListModelRelationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest,
      com.aiflow.proto.Message.Response> getRegisterModelRelationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerModelRelation",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest,
      com.aiflow.proto.Message.Response> getRegisterModelRelationMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest, com.aiflow.proto.Message.Response> getRegisterModelRelationMethod;
    if ((getRegisterModelRelationMethod = MetadataServiceGrpc.getRegisterModelRelationMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterModelRelationMethod = MetadataServiceGrpc.getRegisterModelRelationMethod) == null) {
          MetadataServiceGrpc.getRegisterModelRelationMethod = getRegisterModelRelationMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerModelRelation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerModelRelation"))
              .build();
        }
      }
    }
    return getRegisterModelRelationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteModelRelationByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelRelationById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteModelRelationByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteModelRelationByIdMethod;
    if ((getDeleteModelRelationByIdMethod = MetadataServiceGrpc.getDeleteModelRelationByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelRelationByIdMethod = MetadataServiceGrpc.getDeleteModelRelationByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteModelRelationByIdMethod = getDeleteModelRelationByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelRelationById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelRelationById"))
              .build();
        }
      }
    }
    return getDeleteModelRelationByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelRelationByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelRelationByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelRelationByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteModelRelationByNameMethod;
    if ((getDeleteModelRelationByNameMethod = MetadataServiceGrpc.getDeleteModelRelationByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelRelationByNameMethod = MetadataServiceGrpc.getDeleteModelRelationByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteModelRelationByNameMethod = getDeleteModelRelationByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelRelationByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelRelationByName"))
              .build();
        }
      }
    }
    return getDeleteModelRelationByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetModelByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetModelByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetModelByIdMethod;
    if ((getGetModelByIdMethod = MetadataServiceGrpc.getGetModelByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelByIdMethod = MetadataServiceGrpc.getGetModelByIdMethod) == null) {
          MetadataServiceGrpc.getGetModelByIdMethod = getGetModelByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelById"))
              .build();
        }
      }
    }
    return getGetModelByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetModelByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetModelByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetModelByNameMethod;
    if ((getGetModelByNameMethod = MetadataServiceGrpc.getGetModelByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelByNameMethod = MetadataServiceGrpc.getGetModelByNameMethod) == null) {
          MetadataServiceGrpc.getGetModelByNameMethod = getGetModelByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelByName"))
              .build();
        }
      }
    }
    return getGetModelByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest,
      com.aiflow.proto.Message.Response> getRegisterModelMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerModel",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest,
      com.aiflow.proto.Message.Response> getRegisterModelMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest, com.aiflow.proto.Message.Response> getRegisterModelMethod;
    if ((getRegisterModelMethod = MetadataServiceGrpc.getRegisterModelMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterModelMethod = MetadataServiceGrpc.getRegisterModelMethod) == null) {
          MetadataServiceGrpc.getRegisterModelMethod = getRegisterModelMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerModel"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerModel"))
              .build();
        }
      }
    }
    return getRegisterModelMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteModelByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteModelByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteModelByIdMethod;
    if ((getDeleteModelByIdMethod = MetadataServiceGrpc.getDeleteModelByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelByIdMethod = MetadataServiceGrpc.getDeleteModelByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteModelByIdMethod = getDeleteModelByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelById"))
              .build();
        }
      }
    }
    return getDeleteModelByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteModelByNameMethod;
    if ((getDeleteModelByNameMethod = MetadataServiceGrpc.getDeleteModelByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelByNameMethod = MetadataServiceGrpc.getDeleteModelByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteModelByNameMethod = getDeleteModelByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelByName"))
              .build();
        }
      }
    }
    return getDeleteModelByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionRelationByVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelVersionRelationByVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionRelationByVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response> getGetModelVersionRelationByVersionMethod;
    if ((getGetModelVersionRelationByVersionMethod = MetadataServiceGrpc.getGetModelVersionRelationByVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelVersionRelationByVersionMethod = MetadataServiceGrpc.getGetModelVersionRelationByVersionMethod) == null) {
          MetadataServiceGrpc.getGetModelVersionRelationByVersionMethod = getGetModelVersionRelationByVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelVersionRelationByVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelVersionRelationByVersion"))
              .build();
        }
      }
    }
    return getGetModelVersionRelationByVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest,
      com.aiflow.proto.Message.Response> getListModelVersionRelationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listModelVersionRelation",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest,
      com.aiflow.proto.Message.Response> getListModelVersionRelationMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest, com.aiflow.proto.Message.Response> getListModelVersionRelationMethod;
    if ((getListModelVersionRelationMethod = MetadataServiceGrpc.getListModelVersionRelationMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListModelVersionRelationMethod = MetadataServiceGrpc.getListModelVersionRelationMethod) == null) {
          MetadataServiceGrpc.getListModelVersionRelationMethod = getListModelVersionRelationMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listModelVersionRelation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listModelVersionRelation"))
              .build();
        }
      }
    }
    return getListModelVersionRelationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest,
      com.aiflow.proto.Message.Response> getRegisterModelVersionRelationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerModelVersionRelation",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest,
      com.aiflow.proto.Message.Response> getRegisterModelVersionRelationMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest, com.aiflow.proto.Message.Response> getRegisterModelVersionRelationMethod;
    if ((getRegisterModelVersionRelationMethod = MetadataServiceGrpc.getRegisterModelVersionRelationMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterModelVersionRelationMethod = MetadataServiceGrpc.getRegisterModelVersionRelationMethod) == null) {
          MetadataServiceGrpc.getRegisterModelVersionRelationMethod = getRegisterModelVersionRelationMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerModelVersionRelation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerModelVersionRelation"))
              .build();
        }
      }
    }
    return getRegisterModelVersionRelationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionRelationByVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelVersionRelationByVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionRelationByVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response> getDeleteModelVersionRelationByVersionMethod;
    if ((getDeleteModelVersionRelationByVersionMethod = MetadataServiceGrpc.getDeleteModelVersionRelationByVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelVersionRelationByVersionMethod = MetadataServiceGrpc.getDeleteModelVersionRelationByVersionMethod) == null) {
          MetadataServiceGrpc.getDeleteModelVersionRelationByVersionMethod = getDeleteModelVersionRelationByVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelVersionRelationByVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelVersionRelationByVersion"))
              .build();
        }
      }
    }
    return getDeleteModelVersionRelationByVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionByVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelVersionByVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionByVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response> getGetModelVersionByVersionMethod;
    if ((getGetModelVersionByVersionMethod = MetadataServiceGrpc.getGetModelVersionByVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetModelVersionByVersionMethod = MetadataServiceGrpc.getGetModelVersionByVersionMethod) == null) {
          MetadataServiceGrpc.getGetModelVersionByVersionMethod = getGetModelVersionByVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelVersionByVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getModelVersionByVersion"))
              .build();
        }
      }
    }
    return getGetModelVersionByVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest,
      com.aiflow.proto.Message.Response> getRegisterModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerModelVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest,
      com.aiflow.proto.Message.Response> getRegisterModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest, com.aiflow.proto.Message.Response> getRegisterModelVersionMethod;
    if ((getRegisterModelVersionMethod = MetadataServiceGrpc.getRegisterModelVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterModelVersionMethod = MetadataServiceGrpc.getRegisterModelVersionMethod) == null) {
          MetadataServiceGrpc.getRegisterModelVersionMethod = getRegisterModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerModelVersion"))
              .build();
        }
      }
    }
    return getRegisterModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionByVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelVersionByVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionByVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response> getDeleteModelVersionByVersionMethod;
    if ((getDeleteModelVersionByVersionMethod = MetadataServiceGrpc.getDeleteModelVersionByVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteModelVersionByVersionMethod = MetadataServiceGrpc.getDeleteModelVersionByVersionMethod) == null) {
          MetadataServiceGrpc.getDeleteModelVersionByVersionMethod = getDeleteModelVersionByVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelVersionByVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteModelVersionByVersion"))
              .build();
        }
      }
    }
    return getDeleteModelVersionByVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetDeployedModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getDeployedModelVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetDeployedModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response> getGetDeployedModelVersionMethod;
    if ((getGetDeployedModelVersionMethod = MetadataServiceGrpc.getGetDeployedModelVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetDeployedModelVersionMethod = MetadataServiceGrpc.getGetDeployedModelVersionMethod) == null) {
          MetadataServiceGrpc.getGetDeployedModelVersionMethod = getGetDeployedModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getDeployedModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getDeployedModelVersion"))
              .build();
        }
      }
    }
    return getGetDeployedModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetLatestValidatedModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getLatestValidatedModelVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetLatestValidatedModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response> getGetLatestValidatedModelVersionMethod;
    if ((getGetLatestValidatedModelVersionMethod = MetadataServiceGrpc.getGetLatestValidatedModelVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetLatestValidatedModelVersionMethod = MetadataServiceGrpc.getGetLatestValidatedModelVersionMethod) == null) {
          MetadataServiceGrpc.getGetLatestValidatedModelVersionMethod = getGetLatestValidatedModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getLatestValidatedModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getLatestValidatedModelVersion"))
              .build();
        }
      }
    }
    return getGetLatestValidatedModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetLatestGeneratedModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getLatestGeneratedModelVersion",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
      com.aiflow.proto.Message.Response> getGetLatestGeneratedModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response> getGetLatestGeneratedModelVersionMethod;
    if ((getGetLatestGeneratedModelVersionMethod = MetadataServiceGrpc.getGetLatestGeneratedModelVersionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetLatestGeneratedModelVersionMethod = MetadataServiceGrpc.getGetLatestGeneratedModelVersionMethod) == null) {
          MetadataServiceGrpc.getGetLatestGeneratedModelVersionMethod = getGetLatestGeneratedModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getLatestGeneratedModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getLatestGeneratedModelVersion"))
              .build();
        }
      }
    }
    return getGetLatestGeneratedModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetProjectByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getProjectById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetProjectByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetProjectByIdMethod;
    if ((getGetProjectByIdMethod = MetadataServiceGrpc.getGetProjectByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetProjectByIdMethod = MetadataServiceGrpc.getGetProjectByIdMethod) == null) {
          MetadataServiceGrpc.getGetProjectByIdMethod = getGetProjectByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getProjectById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getProjectById"))
              .build();
        }
      }
    }
    return getGetProjectByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetProjectByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getProjectByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetProjectByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetProjectByNameMethod;
    if ((getGetProjectByNameMethod = MetadataServiceGrpc.getGetProjectByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetProjectByNameMethod = MetadataServiceGrpc.getGetProjectByNameMethod) == null) {
          MetadataServiceGrpc.getGetProjectByNameMethod = getGetProjectByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getProjectByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getProjectByName"))
              .build();
        }
      }
    }
    return getGetProjectByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest,
      com.aiflow.proto.Message.Response> getRegisterProjectMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerProject",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest,
      com.aiflow.proto.Message.Response> getRegisterProjectMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest, com.aiflow.proto.Message.Response> getRegisterProjectMethod;
    if ((getRegisterProjectMethod = MetadataServiceGrpc.getRegisterProjectMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterProjectMethod = MetadataServiceGrpc.getRegisterProjectMethod) == null) {
          MetadataServiceGrpc.getRegisterProjectMethod = getRegisterProjectMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerProject"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerProject"))
              .build();
        }
      }
    }
    return getRegisterProjectMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest,
      com.aiflow.proto.Message.Response> getUpdateProjectMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateProject",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest,
      com.aiflow.proto.Message.Response> getUpdateProjectMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest, com.aiflow.proto.Message.Response> getUpdateProjectMethod;
    if ((getUpdateProjectMethod = MetadataServiceGrpc.getUpdateProjectMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateProjectMethod = MetadataServiceGrpc.getUpdateProjectMethod) == null) {
          MetadataServiceGrpc.getUpdateProjectMethod = getUpdateProjectMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateProject"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateProject"))
              .build();
        }
      }
    }
    return getUpdateProjectMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListProjectMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listProject",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListProjectMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListProjectMethod;
    if ((getListProjectMethod = MetadataServiceGrpc.getListProjectMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListProjectMethod = MetadataServiceGrpc.getListProjectMethod) == null) {
          MetadataServiceGrpc.getListProjectMethod = getListProjectMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listProject"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listProject"))
              .build();
        }
      }
    }
    return getListProjectMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteProjectByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteProjectById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteProjectByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteProjectByIdMethod;
    if ((getDeleteProjectByIdMethod = MetadataServiceGrpc.getDeleteProjectByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteProjectByIdMethod = MetadataServiceGrpc.getDeleteProjectByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteProjectByIdMethod = getDeleteProjectByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteProjectById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteProjectById"))
              .build();
        }
      }
    }
    return getDeleteProjectByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteProjectByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteProjectByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteProjectByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteProjectByNameMethod;
    if ((getDeleteProjectByNameMethod = MetadataServiceGrpc.getDeleteProjectByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteProjectByNameMethod = MetadataServiceGrpc.getDeleteProjectByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteProjectByNameMethod = getDeleteProjectByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteProjectByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteProjectByName"))
              .build();
        }
      }
    }
    return getDeleteProjectByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetArtifactByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getArtifactById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetArtifactByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetArtifactByIdMethod;
    if ((getGetArtifactByIdMethod = MetadataServiceGrpc.getGetArtifactByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetArtifactByIdMethod = MetadataServiceGrpc.getGetArtifactByIdMethod) == null) {
          MetadataServiceGrpc.getGetArtifactByIdMethod = getGetArtifactByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getArtifactById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getArtifactById"))
              .build();
        }
      }
    }
    return getGetArtifactByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetArtifactByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getArtifactByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetArtifactByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetArtifactByNameMethod;
    if ((getGetArtifactByNameMethod = MetadataServiceGrpc.getGetArtifactByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetArtifactByNameMethod = MetadataServiceGrpc.getGetArtifactByNameMethod) == null) {
          MetadataServiceGrpc.getGetArtifactByNameMethod = getGetArtifactByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getArtifactByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getArtifactByName"))
              .build();
        }
      }
    }
    return getGetArtifactByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest,
      com.aiflow.proto.Message.Response> getUpdateArtifactMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateArtifact",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest,
      com.aiflow.proto.Message.Response> getUpdateArtifactMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest, com.aiflow.proto.Message.Response> getUpdateArtifactMethod;
    if ((getUpdateArtifactMethod = MetadataServiceGrpc.getUpdateArtifactMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateArtifactMethod = MetadataServiceGrpc.getUpdateArtifactMethod) == null) {
          MetadataServiceGrpc.getUpdateArtifactMethod = getUpdateArtifactMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateArtifact"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateArtifact"))
              .build();
        }
      }
    }
    return getUpdateArtifactMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest,
      com.aiflow.proto.Message.Response> getRegisterArtifactMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerArtifact",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest,
      com.aiflow.proto.Message.Response> getRegisterArtifactMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest, com.aiflow.proto.Message.Response> getRegisterArtifactMethod;
    if ((getRegisterArtifactMethod = MetadataServiceGrpc.getRegisterArtifactMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterArtifactMethod = MetadataServiceGrpc.getRegisterArtifactMethod) == null) {
          MetadataServiceGrpc.getRegisterArtifactMethod = getRegisterArtifactMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerArtifact"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerArtifact"))
              .build();
        }
      }
    }
    return getRegisterArtifactMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListArtifactMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listArtifact",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListArtifactMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListArtifactMethod;
    if ((getListArtifactMethod = MetadataServiceGrpc.getListArtifactMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListArtifactMethod = MetadataServiceGrpc.getListArtifactMethod) == null) {
          MetadataServiceGrpc.getListArtifactMethod = getListArtifactMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listArtifact"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listArtifact"))
              .build();
        }
      }
    }
    return getListArtifactMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteArtifactByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteArtifactById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteArtifactByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteArtifactByIdMethod;
    if ((getDeleteArtifactByIdMethod = MetadataServiceGrpc.getDeleteArtifactByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteArtifactByIdMethod = MetadataServiceGrpc.getDeleteArtifactByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteArtifactByIdMethod = getDeleteArtifactByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteArtifactById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteArtifactById"))
              .build();
        }
      }
    }
    return getDeleteArtifactByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteArtifactByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteArtifactByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteArtifactByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteArtifactByNameMethod;
    if ((getDeleteArtifactByNameMethod = MetadataServiceGrpc.getDeleteArtifactByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteArtifactByNameMethod = MetadataServiceGrpc.getDeleteArtifactByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteArtifactByNameMethod = getDeleteArtifactByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteArtifactByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteArtifactByName"))
              .build();
        }
      }
    }
    return getDeleteArtifactByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest,
      com.aiflow.proto.Message.Response> getRegisterWorkflowMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerWorkflow",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest,
      com.aiflow.proto.Message.Response> getRegisterWorkflowMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest, com.aiflow.proto.Message.Response> getRegisterWorkflowMethod;
    if ((getRegisterWorkflowMethod = MetadataServiceGrpc.getRegisterWorkflowMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterWorkflowMethod = MetadataServiceGrpc.getRegisterWorkflowMethod) == null) {
          MetadataServiceGrpc.getRegisterWorkflowMethod = getRegisterWorkflowMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerWorkflow"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerWorkflow"))
              .build();
        }
      }
    }
    return getRegisterWorkflowMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateWorkflow",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest, com.aiflow.proto.Message.Response> getUpdateWorkflowMethod;
    if ((getUpdateWorkflowMethod = MetadataServiceGrpc.getUpdateWorkflowMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateWorkflowMethod = MetadataServiceGrpc.getUpdateWorkflowMethod) == null) {
          MetadataServiceGrpc.getUpdateWorkflowMethod = getUpdateWorkflowMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateWorkflow"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateWorkflow"))
              .build();
        }
      }
    }
    return getUpdateWorkflowMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetWorkflowByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getWorkflowById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetWorkflowByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetWorkflowByIdMethod;
    if ((getGetWorkflowByIdMethod = MetadataServiceGrpc.getGetWorkflowByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetWorkflowByIdMethod = MetadataServiceGrpc.getGetWorkflowByIdMethod) == null) {
          MetadataServiceGrpc.getGetWorkflowByIdMethod = getGetWorkflowByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getWorkflowById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getWorkflowById"))
              .build();
        }
      }
    }
    return getGetWorkflowByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
      com.aiflow.proto.Message.Response> getGetWorkflowByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getWorkflowByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
      com.aiflow.proto.Message.Response> getGetWorkflowByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest, com.aiflow.proto.Message.Response> getGetWorkflowByNameMethod;
    if ((getGetWorkflowByNameMethod = MetadataServiceGrpc.getGetWorkflowByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetWorkflowByNameMethod = MetadataServiceGrpc.getGetWorkflowByNameMethod) == null) {
          MetadataServiceGrpc.getGetWorkflowByNameMethod = getGetWorkflowByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getWorkflowByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getWorkflowByName"))
              .build();
        }
      }
    }
    return getGetWorkflowByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteWorkflowById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteWorkflowByIdMethod;
    if ((getDeleteWorkflowByIdMethod = MetadataServiceGrpc.getDeleteWorkflowByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteWorkflowByIdMethod = MetadataServiceGrpc.getDeleteWorkflowByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteWorkflowByIdMethod = getDeleteWorkflowByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteWorkflowById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteWorkflowById"))
              .build();
        }
      }
    }
    return getDeleteWorkflowByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteWorkflowByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest, com.aiflow.proto.Message.Response> getDeleteWorkflowByNameMethod;
    if ((getDeleteWorkflowByNameMethod = MetadataServiceGrpc.getDeleteWorkflowByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteWorkflowByNameMethod = MetadataServiceGrpc.getDeleteWorkflowByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteWorkflowByNameMethod = getDeleteWorkflowByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteWorkflowByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteWorkflowByName"))
              .build();
        }
      }
    }
    return getDeleteWorkflowByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest,
      com.aiflow.proto.Message.Response> getListWorkflowsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listWorkflows",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest,
      com.aiflow.proto.Message.Response> getListWorkflowsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest, com.aiflow.proto.Message.Response> getListWorkflowsMethod;
    if ((getListWorkflowsMethod = MetadataServiceGrpc.getListWorkflowsMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListWorkflowsMethod = MetadataServiceGrpc.getListWorkflowsMethod) == null) {
          MetadataServiceGrpc.getListWorkflowsMethod = getListWorkflowsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listWorkflows"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listWorkflows"))
              .build();
        }
      }
    }
    return getListWorkflowsMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static MetadataServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetadataServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetadataServiceStub>() {
        @java.lang.Override
        public MetadataServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetadataServiceStub(channel, callOptions);
        }
      };
    return MetadataServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static MetadataServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetadataServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetadataServiceBlockingStub>() {
        @java.lang.Override
        public MetadataServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetadataServiceBlockingStub(channel, callOptions);
        }
      };
    return MetadataServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static MetadataServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetadataServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetadataServiceFutureStub>() {
        @java.lang.Override
        public MetadataServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetadataServiceFutureStub(channel, callOptions);
        }
      };
    return MetadataServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public static abstract class MetadataServiceImplBase implements io.grpc.BindableService {

    /**
     * <pre>
     *dataset api
     * </pre>
     */
    public void getDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetDatasetByIdMethod(), responseObserver);
    }

    /**
     */
    public void getDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetDatasetByNameMethod(), responseObserver);
    }

    /**
     */
    public void listDatasets(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListDatasetsMethod(), responseObserver);
    }

    /**
     */
    public void registerDataset(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterDatasetMethod(), responseObserver);
    }

    /**
     */
    public void registerDatasetWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterDatasetWithCatalogMethod(), responseObserver);
    }

    /**
     */
    public void registerDatasets(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterDatasetsMethod(), responseObserver);
    }

    /**
     */
    public void updateDataset(com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateDatasetMethod(), responseObserver);
    }

    /**
     */
    public void deleteDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteDatasetByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteDatasetByNameMethod(), responseObserver);
    }

    /**
     * <pre>
     *model relation api
     * </pre>
     */
    public void getModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelRelationByIdMethod(), responseObserver);
    }

    /**
     */
    public void getModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelRelationByNameMethod(), responseObserver);
    }

    /**
     */
    public void listModelRelation(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListModelRelationMethod(), responseObserver);
    }

    /**
     */
    public void registerModelRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterModelRelationMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelRelationByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelRelationByNameMethod(), responseObserver);
    }

    /**
     * <pre>
     *model api
     * </pre>
     */
    public void getModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelByIdMethod(), responseObserver);
    }

    /**
     */
    public void getModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelByNameMethod(), responseObserver);
    }

    /**
     */
    public void registerModel(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterModelMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelByNameMethod(), responseObserver);
    }

    /**
     * <pre>
     *model version relation api
     * </pre>
     */
    public void getModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelVersionRelationByVersionMethod(), responseObserver);
    }

    /**
     */
    public void listModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListModelVersionRelationMethod(), responseObserver);
    }

    /**
     */
    public void registerModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterModelVersionRelationMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelVersionRelationByVersionMethod(), responseObserver);
    }

    /**
     * <pre>
     *model version api
     * </pre>
     */
    public void getModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelVersionByVersionMethod(), responseObserver);
    }

    /**
     */
    public void registerModelVersion(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterModelVersionMethod(), responseObserver);
    }

    /**
     */
    public void deleteModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelVersionByVersionMethod(), responseObserver);
    }

    /**
     */
    public void getDeployedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetDeployedModelVersionMethod(), responseObserver);
    }

    /**
     */
    public void getLatestValidatedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetLatestValidatedModelVersionMethod(), responseObserver);
    }

    /**
     */
    public void getLatestGeneratedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetLatestGeneratedModelVersionMethod(), responseObserver);
    }

    /**
     * <pre>
     *project api
     * </pre>
     */
    public void getProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetProjectByIdMethod(), responseObserver);
    }

    /**
     */
    public void getProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetProjectByNameMethod(), responseObserver);
    }

    /**
     */
    public void registerProject(com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterProjectMethod(), responseObserver);
    }

    /**
     */
    public void updateProject(com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateProjectMethod(), responseObserver);
    }

    /**
     */
    public void listProject(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListProjectMethod(), responseObserver);
    }

    /**
     */
    public void deleteProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteProjectByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteProjectByNameMethod(), responseObserver);
    }

    /**
     * <pre>
     *artifact api
     * </pre>
     */
    public void getArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetArtifactByIdMethod(), responseObserver);
    }

    /**
     */
    public void getArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetArtifactByNameMethod(), responseObserver);
    }

    /**
     */
    public void updateArtifact(com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateArtifactMethod(), responseObserver);
    }

    /**
     */
    public void registerArtifact(com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterArtifactMethod(), responseObserver);
    }

    /**
     */
    public void listArtifact(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListArtifactMethod(), responseObserver);
    }

    /**
     */
    public void deleteArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteArtifactByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteArtifactByNameMethod(), responseObserver);
    }

    /**
     */
    public void registerWorkflow(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterWorkflowMethod(), responseObserver);
    }

    /**
     */
    public void updateWorkflow(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateWorkflowMethod(), responseObserver);
    }

    /**
     */
    public void getWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetWorkflowByIdMethod(), responseObserver);
    }

    /**
     */
    public void getWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetWorkflowByNameMethod(), responseObserver);
    }

    /**
     */
    public void deleteWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteWorkflowByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteWorkflowByNameMethod(), responseObserver);
    }

    /**
     */
    public void listWorkflows(com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListWorkflowsMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getGetDatasetByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_DATASET_BY_ID)))
          .addMethod(
            getGetDatasetByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_DATASET_BY_NAME)))
          .addMethod(
            getListDatasetsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_DATASETS)))
          .addMethod(
            getRegisterDatasetMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_DATASET)))
          .addMethod(
            getRegisterDatasetWithCatalogMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_DATASET_WITH_CATALOG)))
          .addMethod(
            getRegisterDatasetsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_DATASETS)))
          .addMethod(
            getUpdateDatasetMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_DATASET)))
          .addMethod(
            getDeleteDatasetByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_DATASET_BY_ID)))
          .addMethod(
            getDeleteDatasetByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_DATASET_BY_NAME)))
          .addMethod(
            getGetModelRelationByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_RELATION_BY_ID)))
          .addMethod(
            getGetModelRelationByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_RELATION_BY_NAME)))
          .addMethod(
            getListModelRelationMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_MODEL_RELATION)))
          .addMethod(
            getRegisterModelRelationMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_MODEL_RELATION)))
          .addMethod(
            getDeleteModelRelationByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_RELATION_BY_ID)))
          .addMethod(
            getDeleteModelRelationByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_RELATION_BY_NAME)))
          .addMethod(
            getGetModelByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_BY_ID)))
          .addMethod(
            getGetModelByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_BY_NAME)))
          .addMethod(
            getRegisterModelMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_MODEL)))
          .addMethod(
            getDeleteModelByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_BY_ID)))
          .addMethod(
            getDeleteModelByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_BY_NAME)))
          .addMethod(
            getGetModelVersionRelationByVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_VERSION_RELATION_BY_VERSION)))
          .addMethod(
            getListModelVersionRelationMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_MODEL_VERSION_RELATION)))
          .addMethod(
            getRegisterModelVersionRelationMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_MODEL_VERSION_RELATION)))
          .addMethod(
            getDeleteModelVersionRelationByVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_VERSION_RELATION_BY_VERSION)))
          .addMethod(
            getGetModelVersionByVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_VERSION_BY_VERSION)))
          .addMethod(
            getRegisterModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_MODEL_VERSION)))
          .addMethod(
            getDeleteModelVersionByVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_VERSION_BY_VERSION)))
          .addMethod(
            getGetDeployedModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_DEPLOYED_MODEL_VERSION)))
          .addMethod(
            getGetLatestValidatedModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_LATEST_VALIDATED_MODEL_VERSION)))
          .addMethod(
            getGetLatestGeneratedModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_LATEST_GENERATED_MODEL_VERSION)))
          .addMethod(
            getGetProjectByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_PROJECT_BY_ID)))
          .addMethod(
            getGetProjectByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_PROJECT_BY_NAME)))
          .addMethod(
            getRegisterProjectMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_PROJECT)))
          .addMethod(
            getUpdateProjectMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_PROJECT)))
          .addMethod(
            getListProjectMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_PROJECT)))
          .addMethod(
            getDeleteProjectByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_PROJECT_BY_ID)))
          .addMethod(
            getDeleteProjectByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_PROJECT_BY_NAME)))
          .addMethod(
            getGetArtifactByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_ARTIFACT_BY_ID)))
          .addMethod(
            getGetArtifactByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_ARTIFACT_BY_NAME)))
          .addMethod(
            getUpdateArtifactMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_ARTIFACT)))
          .addMethod(
            getRegisterArtifactMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_ARTIFACT)))
          .addMethod(
            getListArtifactMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_ARTIFACT)))
          .addMethod(
            getDeleteArtifactByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_ARTIFACT_BY_ID)))
          .addMethod(
            getDeleteArtifactByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_ARTIFACT_BY_NAME)))
          .addMethod(
            getRegisterWorkflowMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_WORKFLOW)))
          .addMethod(
            getUpdateWorkflowMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_WORKFLOW)))
          .addMethod(
            getGetWorkflowByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_WORKFLOW_BY_ID)))
          .addMethod(
            getGetWorkflowByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_WORKFLOW_BY_NAME)))
          .addMethod(
            getDeleteWorkflowByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_WORKFLOW_BY_ID)))
          .addMethod(
            getDeleteWorkflowByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_WORKFLOW_BY_NAME)))
          .addMethod(
            getListWorkflowsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_WORKFLOWS)))
          .build();
    }
  }

  /**
   */
  public static final class MetadataServiceStub extends io.grpc.stub.AbstractAsyncStub<MetadataServiceStub> {
    private MetadataServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetadataServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetadataServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     *dataset api
     * </pre>
     */
    public void getDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetDatasetByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetDatasetByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listDatasets(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListDatasetsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerDataset(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterDatasetMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerDatasetWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterDatasetWithCatalogMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerDatasets(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterDatasetsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateDataset(com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateDatasetMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteDatasetByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteDatasetByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *model relation api
     * </pre>
     */
    public void getModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelRelationByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelRelationByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listModelRelation(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListModelRelationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerModelRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterModelRelationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelRelationByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelRelationByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *model api
     * </pre>
     */
    public void getModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerModel(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterModelMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *model version relation api
     * </pre>
     */
    public void getModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelVersionRelationByVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListModelVersionRelationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterModelVersionRelationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelVersionRelationByVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *model version api
     * </pre>
     */
    public void getModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelVersionByVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerModelVersion(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelVersionByVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getDeployedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetDeployedModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getLatestValidatedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetLatestValidatedModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getLatestGeneratedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetLatestGeneratedModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *project api
     * </pre>
     */
    public void getProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetProjectByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetProjectByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerProject(com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterProjectMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateProject(com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateProjectMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listProject(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListProjectMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteProjectByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteProjectByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *artifact api
     * </pre>
     */
    public void getArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetArtifactByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetArtifactByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateArtifact(com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateArtifactMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerArtifact(com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterArtifactMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listArtifact(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListArtifactMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteArtifactByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteArtifactByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerWorkflow(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterWorkflowMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateWorkflow(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateWorkflowMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetWorkflowByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetWorkflowByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteWorkflowByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteWorkflowByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listWorkflows(com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListWorkflowsMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   */
  public static final class MetadataServiceBlockingStub extends io.grpc.stub.AbstractBlockingStub<MetadataServiceBlockingStub> {
    private MetadataServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetadataServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetadataServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     *dataset api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetDatasetByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetDatasetByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listDatasets(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListDatasetsMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerDataset(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterDatasetMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerDatasetWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterDatasetWithCatalogMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerDatasets(com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterDatasetsMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateDataset(com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateDatasetMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteDatasetById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteDatasetByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteDatasetByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteDatasetByNameMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *model relation api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelRelationByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelRelationByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listModelRelation(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListModelRelationMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerModelRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterModelRelationMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelRelationById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelRelationByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelRelationByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelRelationByNameMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *model api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerModel(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterModelMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelByNameMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *model version relation api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelVersionRelationByVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest request) {
      return blockingUnaryCall(
          getChannel(), getListModelVersionRelationMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerModelVersionRelation(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterModelVersionRelationMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelVersionRelationByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelVersionRelationByVersionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *model version api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelVersionByVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerModelVersion(com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterModelVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteModelVersionByVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelVersionByVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getDeployedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetDeployedModelVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getLatestValidatedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetLatestValidatedModelVersionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getLatestGeneratedModelVersion(com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetLatestGeneratedModelVersionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *project api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetProjectByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetProjectByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerProject(com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterProjectMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateProject(com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateProjectMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listProject(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListProjectMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteProjectById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteProjectByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteProjectByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteProjectByNameMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *artifact api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetArtifactByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetArtifactByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateArtifact(com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateArtifactMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerArtifact(com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterArtifactMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listArtifact(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListArtifactMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteArtifactById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteArtifactByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteArtifactByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteArtifactByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerWorkflow(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterWorkflowMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateWorkflow(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateWorkflowMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetWorkflowByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetWorkflowByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteWorkflowById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteWorkflowByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteWorkflowByName(com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteWorkflowByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listWorkflows(com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest request) {
      return blockingUnaryCall(
          getChannel(), getListWorkflowsMethod(), getCallOptions(), request);
    }
  }

  /**
   */
  public static final class MetadataServiceFutureStub extends io.grpc.stub.AbstractFutureStub<MetadataServiceFutureStub> {
    private MetadataServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetadataServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetadataServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     *dataset api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getDatasetById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetDatasetByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getDatasetByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetDatasetByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listDatasets(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListDatasetsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerDataset(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterDatasetMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerDatasetWithCatalog(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterDatasetWithCatalogMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerDatasets(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterDatasetsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateDataset(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateDatasetMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteDatasetById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteDatasetByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteDatasetByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteDatasetByNameMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *model relation api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelRelationById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelRelationByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelRelationByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelRelationByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listModelRelation(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListModelRelationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerModelRelation(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterModelRelationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelRelationById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelRelationByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelRelationByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelRelationByNameMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *model api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerModel(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterModelMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelByNameMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *model version relation api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelVersionRelationByVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelVersionRelationByVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listModelVersionRelation(
        com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListModelVersionRelationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerModelVersionRelation(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterModelVersionRelationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelVersionRelationByVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelVersionRelationByVersionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *model version api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelVersionByVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelVersionByVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerModelVersion(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterModelVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelVersionByVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelVersionByVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getDeployedModelVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetDeployedModelVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getLatestValidatedModelVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetLatestValidatedModelVersionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getLatestGeneratedModelVersion(
        com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetLatestGeneratedModelVersionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *project api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getProjectById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetProjectByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getProjectByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetProjectByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerProject(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterProjectMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateProject(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateProjectMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listProject(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListProjectMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteProjectById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteProjectByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteProjectByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteProjectByNameMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *artifact api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getArtifactById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetArtifactByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getArtifactByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetArtifactByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateArtifact(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateArtifactMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerArtifact(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterArtifactMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listArtifact(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListArtifactMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteArtifactById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteArtifactByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteArtifactByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteArtifactByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerWorkflow(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterWorkflowMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateWorkflow(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateWorkflowMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getWorkflowById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetWorkflowByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getWorkflowByName(
        com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetWorkflowByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteWorkflowById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteWorkflowByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteWorkflowByName(
        com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteWorkflowByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listWorkflows(
        com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListWorkflowsMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_GET_DATASET_BY_ID = 0;
  private static final int METHODID_GET_DATASET_BY_NAME = 1;
  private static final int METHODID_LIST_DATASETS = 2;
  private static final int METHODID_REGISTER_DATASET = 3;
  private static final int METHODID_REGISTER_DATASET_WITH_CATALOG = 4;
  private static final int METHODID_REGISTER_DATASETS = 5;
  private static final int METHODID_UPDATE_DATASET = 6;
  private static final int METHODID_DELETE_DATASET_BY_ID = 7;
  private static final int METHODID_DELETE_DATASET_BY_NAME = 8;
  private static final int METHODID_GET_MODEL_RELATION_BY_ID = 9;
  private static final int METHODID_GET_MODEL_RELATION_BY_NAME = 10;
  private static final int METHODID_LIST_MODEL_RELATION = 11;
  private static final int METHODID_REGISTER_MODEL_RELATION = 12;
  private static final int METHODID_DELETE_MODEL_RELATION_BY_ID = 13;
  private static final int METHODID_DELETE_MODEL_RELATION_BY_NAME = 14;
  private static final int METHODID_GET_MODEL_BY_ID = 15;
  private static final int METHODID_GET_MODEL_BY_NAME = 16;
  private static final int METHODID_REGISTER_MODEL = 17;
  private static final int METHODID_DELETE_MODEL_BY_ID = 18;
  private static final int METHODID_DELETE_MODEL_BY_NAME = 19;
  private static final int METHODID_GET_MODEL_VERSION_RELATION_BY_VERSION = 20;
  private static final int METHODID_LIST_MODEL_VERSION_RELATION = 21;
  private static final int METHODID_REGISTER_MODEL_VERSION_RELATION = 22;
  private static final int METHODID_DELETE_MODEL_VERSION_RELATION_BY_VERSION = 23;
  private static final int METHODID_GET_MODEL_VERSION_BY_VERSION = 24;
  private static final int METHODID_REGISTER_MODEL_VERSION = 25;
  private static final int METHODID_DELETE_MODEL_VERSION_BY_VERSION = 26;
  private static final int METHODID_GET_DEPLOYED_MODEL_VERSION = 27;
  private static final int METHODID_GET_LATEST_VALIDATED_MODEL_VERSION = 28;
  private static final int METHODID_GET_LATEST_GENERATED_MODEL_VERSION = 29;
  private static final int METHODID_GET_PROJECT_BY_ID = 30;
  private static final int METHODID_GET_PROJECT_BY_NAME = 31;
  private static final int METHODID_REGISTER_PROJECT = 32;
  private static final int METHODID_UPDATE_PROJECT = 33;
  private static final int METHODID_LIST_PROJECT = 34;
  private static final int METHODID_DELETE_PROJECT_BY_ID = 35;
  private static final int METHODID_DELETE_PROJECT_BY_NAME = 36;
  private static final int METHODID_GET_ARTIFACT_BY_ID = 37;
  private static final int METHODID_GET_ARTIFACT_BY_NAME = 38;
  private static final int METHODID_UPDATE_ARTIFACT = 39;
  private static final int METHODID_REGISTER_ARTIFACT = 40;
  private static final int METHODID_LIST_ARTIFACT = 41;
  private static final int METHODID_DELETE_ARTIFACT_BY_ID = 42;
  private static final int METHODID_DELETE_ARTIFACT_BY_NAME = 43;
  private static final int METHODID_REGISTER_WORKFLOW = 44;
  private static final int METHODID_UPDATE_WORKFLOW = 45;
  private static final int METHODID_GET_WORKFLOW_BY_ID = 46;
  private static final int METHODID_GET_WORKFLOW_BY_NAME = 47;
  private static final int METHODID_DELETE_WORKFLOW_BY_ID = 48;
  private static final int METHODID_DELETE_WORKFLOW_BY_NAME = 49;
  private static final int METHODID_LIST_WORKFLOWS = 50;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final MetadataServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(MetadataServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_GET_DATASET_BY_ID:
          serviceImpl.getDatasetById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_DATASET_BY_NAME:
          serviceImpl.getDatasetByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_DATASETS:
          serviceImpl.listDatasets((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_DATASET:
          serviceImpl.registerDataset((com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_DATASET_WITH_CATALOG:
          serviceImpl.registerDatasetWithCatalog((com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_DATASETS:
          serviceImpl.registerDatasets((com.aiflow.proto.MetadataServiceOuterClass.RegisterDatasetsRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_DATASET:
          serviceImpl.updateDataset((com.aiflow.proto.MetadataServiceOuterClass.UpdateDatasetRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_DATASET_BY_ID:
          serviceImpl.deleteDatasetById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_DATASET_BY_NAME:
          serviceImpl.deleteDatasetByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_RELATION_BY_ID:
          serviceImpl.getModelRelationById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_RELATION_BY_NAME:
          serviceImpl.getModelRelationByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_MODEL_RELATION:
          serviceImpl.listModelRelation((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_MODEL_RELATION:
          serviceImpl.registerModelRelation((com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRelationRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_RELATION_BY_ID:
          serviceImpl.deleteModelRelationById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_RELATION_BY_NAME:
          serviceImpl.deleteModelRelationByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_BY_ID:
          serviceImpl.getModelById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_BY_NAME:
          serviceImpl.getModelByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_MODEL:
          serviceImpl.registerModel((com.aiflow.proto.MetadataServiceOuterClass.RegisterModelRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_BY_ID:
          serviceImpl.deleteModelById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_BY_NAME:
          serviceImpl.deleteModelByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_VERSION_RELATION_BY_VERSION:
          serviceImpl.getModelVersionRelationByVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_MODEL_VERSION_RELATION:
          serviceImpl.listModelVersionRelation((com.aiflow.proto.MetadataServiceOuterClass.ListModelVersionRelationRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_MODEL_VERSION_RELATION:
          serviceImpl.registerModelVersionRelation((com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRelationRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_VERSION_RELATION_BY_VERSION:
          serviceImpl.deleteModelVersionRelationByVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_VERSION_BY_VERSION:
          serviceImpl.getModelVersionByVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_MODEL_VERSION:
          serviceImpl.registerModelVersion((com.aiflow.proto.MetadataServiceOuterClass.RegisterModelVersionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_VERSION_BY_VERSION:
          serviceImpl.deleteModelVersionByVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelVersionNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_DEPLOYED_MODEL_VERSION:
          serviceImpl.getDeployedModelVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_LATEST_VALIDATED_MODEL_VERSION:
          serviceImpl.getLatestValidatedModelVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_LATEST_GENERATED_MODEL_VERSION:
          serviceImpl.getLatestGeneratedModelVersion((com.aiflow.proto.MetadataServiceOuterClass.ModelNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_PROJECT_BY_ID:
          serviceImpl.getProjectById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_PROJECT_BY_NAME:
          serviceImpl.getProjectByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_PROJECT:
          serviceImpl.registerProject((com.aiflow.proto.MetadataServiceOuterClass.RegisterProjectRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_PROJECT:
          serviceImpl.updateProject((com.aiflow.proto.MetadataServiceOuterClass.UpdateProjectRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_PROJECT:
          serviceImpl.listProject((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_PROJECT_BY_ID:
          serviceImpl.deleteProjectById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_PROJECT_BY_NAME:
          serviceImpl.deleteProjectByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_ARTIFACT_BY_ID:
          serviceImpl.getArtifactById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_ARTIFACT_BY_NAME:
          serviceImpl.getArtifactByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_ARTIFACT:
          serviceImpl.updateArtifact((com.aiflow.proto.MetadataServiceOuterClass.UpdateArtifactRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_ARTIFACT:
          serviceImpl.registerArtifact((com.aiflow.proto.MetadataServiceOuterClass.RegisterArtifactRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_ARTIFACT:
          serviceImpl.listArtifact((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_ARTIFACT_BY_ID:
          serviceImpl.deleteArtifactById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_ARTIFACT_BY_NAME:
          serviceImpl.deleteArtifactByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_WORKFLOW:
          serviceImpl.registerWorkflow((com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkflowRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_WORKFLOW:
          serviceImpl.updateWorkflow((com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_WORKFLOW_BY_ID:
          serviceImpl.getWorkflowById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_WORKFLOW_BY_NAME:
          serviceImpl.getWorkflowByName((com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_WORKFLOW_BY_ID:
          serviceImpl.deleteWorkflowById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_WORKFLOW_BY_NAME:
          serviceImpl.deleteWorkflowByName((com.aiflow.proto.MetadataServiceOuterClass.WorkflowNameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_WORKFLOWS:
          serviceImpl.listWorkflows((com.aiflow.proto.MetadataServiceOuterClass.ListWorkflowsRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  private static abstract class MetadataServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    MetadataServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.aiflow.proto.MetadataServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("MetadataService");
    }
  }

  private static final class MetadataServiceFileDescriptorSupplier
      extends MetadataServiceBaseDescriptorSupplier {
    MetadataServiceFileDescriptorSupplier() {}
  }

  private static final class MetadataServiceMethodDescriptorSupplier
      extends MetadataServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    MetadataServiceMethodDescriptorSupplier(String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (MetadataServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new MetadataServiceFileDescriptorSupplier())
              .addMethod(getGetDatasetByIdMethod())
              .addMethod(getGetDatasetByNameMethod())
              .addMethod(getListDatasetsMethod())
              .addMethod(getRegisterDatasetMethod())
              .addMethod(getRegisterDatasetWithCatalogMethod())
              .addMethod(getRegisterDatasetsMethod())
              .addMethod(getUpdateDatasetMethod())
              .addMethod(getDeleteDatasetByIdMethod())
              .addMethod(getDeleteDatasetByNameMethod())
              .addMethod(getGetModelRelationByIdMethod())
              .addMethod(getGetModelRelationByNameMethod())
              .addMethod(getListModelRelationMethod())
              .addMethod(getRegisterModelRelationMethod())
              .addMethod(getDeleteModelRelationByIdMethod())
              .addMethod(getDeleteModelRelationByNameMethod())
              .addMethod(getGetModelByIdMethod())
              .addMethod(getGetModelByNameMethod())
              .addMethod(getRegisterModelMethod())
              .addMethod(getDeleteModelByIdMethod())
              .addMethod(getDeleteModelByNameMethod())
              .addMethod(getGetModelVersionRelationByVersionMethod())
              .addMethod(getListModelVersionRelationMethod())
              .addMethod(getRegisterModelVersionRelationMethod())
              .addMethod(getDeleteModelVersionRelationByVersionMethod())
              .addMethod(getGetModelVersionByVersionMethod())
              .addMethod(getRegisterModelVersionMethod())
              .addMethod(getDeleteModelVersionByVersionMethod())
              .addMethod(getGetDeployedModelVersionMethod())
              .addMethod(getGetLatestValidatedModelVersionMethod())
              .addMethod(getGetLatestGeneratedModelVersionMethod())
              .addMethod(getGetProjectByIdMethod())
              .addMethod(getGetProjectByNameMethod())
              .addMethod(getRegisterProjectMethod())
              .addMethod(getUpdateProjectMethod())
              .addMethod(getListProjectMethod())
              .addMethod(getDeleteProjectByIdMethod())
              .addMethod(getDeleteProjectByNameMethod())
              .addMethod(getGetArtifactByIdMethod())
              .addMethod(getGetArtifactByNameMethod())
              .addMethod(getUpdateArtifactMethod())
              .addMethod(getRegisterArtifactMethod())
              .addMethod(getListArtifactMethod())
              .addMethod(getDeleteArtifactByIdMethod())
              .addMethod(getDeleteArtifactByNameMethod())
              .addMethod(getRegisterWorkflowMethod())
              .addMethod(getUpdateWorkflowMethod())
              .addMethod(getGetWorkflowByIdMethod())
              .addMethod(getGetWorkflowByNameMethod())
              .addMethod(getDeleteWorkflowByIdMethod())
              .addMethod(getDeleteWorkflowByNameMethod())
              .addMethod(getListWorkflowsMethod())
              .build();
        }
      }
    }
    return result;
  }
}
