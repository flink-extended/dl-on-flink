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
package org.aiflow.client.proto;

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
    comments = "Source: metric_service.proto")
public final class MetricServiceGrpc {

  private MetricServiceGrpc() {}

  public static final String SERVICE_NAME = "ai_flow.MetricService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getRegisterMetricMetaMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerMetricMeta",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getRegisterMetricMetaMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getRegisterMetricMetaMethod;
    if ((getRegisterMetricMetaMethod = MetricServiceGrpc.getRegisterMetricMetaMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getRegisterMetricMetaMethod = MetricServiceGrpc.getRegisterMetricMetaMethod) == null) {
          MetricServiceGrpc.getRegisterMetricMetaMethod = getRegisterMetricMetaMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerMetricMeta"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("registerMetricMeta"))
              .build();
        }
      }
    }
    return getRegisterMetricMetaMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getUpdateMetricMetaMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateMetricMeta",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getUpdateMetricMetaMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getUpdateMetricMetaMethod;
    if ((getUpdateMetricMetaMethod = MetricServiceGrpc.getUpdateMetricMetaMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getUpdateMetricMetaMethod = MetricServiceGrpc.getUpdateMetricMetaMethod) == null) {
          MetricServiceGrpc.getUpdateMetricMetaMethod = getUpdateMetricMetaMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateMetricMeta"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("updateMetricMeta"))
              .build();
        }
      }
    }
    return getUpdateMetricMetaMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
      org.aiflow.client.proto.Message.Response> getDeleteMetricMetaMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteMetricMeta",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest.class,
      responseType = org.aiflow.client.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
      org.aiflow.client.proto.Message.Response> getDeleteMetricMetaMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest, org.aiflow.client.proto.Message.Response> getDeleteMetricMetaMethod;
    if ((getDeleteMetricMetaMethod = MetricServiceGrpc.getDeleteMetricMetaMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getDeleteMetricMetaMethod = MetricServiceGrpc.getDeleteMetricMetaMethod) == null) {
          MetricServiceGrpc.getDeleteMetricMetaMethod = getDeleteMetricMetaMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest, org.aiflow.client.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteMetricMeta"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("deleteMetricMeta"))
              .build();
        }
      }
    }
    return getDeleteMetricMetaMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getGetMetricMetaMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getMetricMeta",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getGetMetricMetaMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getGetMetricMetaMethod;
    if ((getGetMetricMetaMethod = MetricServiceGrpc.getGetMetricMetaMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getGetMetricMetaMethod = MetricServiceGrpc.getGetMetricMetaMethod) == null) {
          MetricServiceGrpc.getGetMetricMetaMethod = getGetMetricMetaMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getMetricMeta"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("getMetricMeta"))
              .build();
        }
      }
    }
    return getGetMetricMetaMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListDatasetMetricMetasMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listDatasetMetricMetas",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListDatasetMetricMetasMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListDatasetMetricMetasMethod;
    if ((getListDatasetMetricMetasMethod = MetricServiceGrpc.getListDatasetMetricMetasMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getListDatasetMetricMetasMethod = MetricServiceGrpc.getListDatasetMetricMetasMethod) == null) {
          MetricServiceGrpc.getListDatasetMetricMetasMethod = getListDatasetMetricMetasMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listDatasetMetricMetas"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("listDatasetMetricMetas"))
              .build();
        }
      }
    }
    return getListDatasetMetricMetasMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListModelMetricMetasMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listModelMetricMetas",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListModelMetricMetasMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> getListModelMetricMetasMethod;
    if ((getListModelMetricMetasMethod = MetricServiceGrpc.getListModelMetricMetasMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getListModelMetricMetasMethod = MetricServiceGrpc.getListModelMetricMetasMethod) == null) {
          MetricServiceGrpc.getListModelMetricMetasMethod = getListModelMetricMetasMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listModelMetricMetas"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("listModelMetricMetas"))
              .build();
        }
      }
    }
    return getListModelMetricMetasMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getRegisterMetricSummaryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerMetricSummary",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getRegisterMetricSummaryMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getRegisterMetricSummaryMethod;
    if ((getRegisterMetricSummaryMethod = MetricServiceGrpc.getRegisterMetricSummaryMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getRegisterMetricSummaryMethod = MetricServiceGrpc.getRegisterMetricSummaryMethod) == null) {
          MetricServiceGrpc.getRegisterMetricSummaryMethod = getRegisterMetricSummaryMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerMetricSummary"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("registerMetricSummary"))
              .build();
        }
      }
    }
    return getRegisterMetricSummaryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getUpdateMetricSummaryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateMetricSummary",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getUpdateMetricSummaryMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getUpdateMetricSummaryMethod;
    if ((getUpdateMetricSummaryMethod = MetricServiceGrpc.getUpdateMetricSummaryMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getUpdateMetricSummaryMethod = MetricServiceGrpc.getUpdateMetricSummaryMethod) == null) {
          MetricServiceGrpc.getUpdateMetricSummaryMethod = getUpdateMetricSummaryMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateMetricSummary"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("updateMetricSummary"))
              .build();
        }
      }
    }
    return getUpdateMetricSummaryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
      org.aiflow.client.proto.Message.Response> getDeleteMetricSummaryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteMetricSummary",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest.class,
      responseType = org.aiflow.client.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
      org.aiflow.client.proto.Message.Response> getDeleteMetricSummaryMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest, org.aiflow.client.proto.Message.Response> getDeleteMetricSummaryMethod;
    if ((getDeleteMetricSummaryMethod = MetricServiceGrpc.getDeleteMetricSummaryMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getDeleteMetricSummaryMethod = MetricServiceGrpc.getDeleteMetricSummaryMethod) == null) {
          MetricServiceGrpc.getDeleteMetricSummaryMethod = getDeleteMetricSummaryMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest, org.aiflow.client.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteMetricSummary"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("deleteMetricSummary"))
              .build();
        }
      }
    }
    return getDeleteMetricSummaryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getGetMetricSummaryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getMetricSummary",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getGetMetricSummaryMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getGetMetricSummaryMethod;
    if ((getGetMetricSummaryMethod = MetricServiceGrpc.getGetMetricSummaryMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getGetMetricSummaryMethod = MetricServiceGrpc.getGetMetricSummaryMethod) == null) {
          MetricServiceGrpc.getGetMetricSummaryMethod = getGetMetricSummaryMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest, org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getMetricSummary"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("getMetricSummary"))
              .build();
        }
      }
    }
    return getGetMetricSummaryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> getListMetricSummariesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listMetricSummaries",
      requestType = org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest.class,
      responseType = org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest,
      org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> getListMetricSummariesMethod() {
    io.grpc.MethodDescriptor<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> getListMetricSummariesMethod;
    if ((getListMetricSummariesMethod = MetricServiceGrpc.getListMetricSummariesMethod) == null) {
      synchronized (MetricServiceGrpc.class) {
        if ((getListMetricSummariesMethod = MetricServiceGrpc.getListMetricSummariesMethod) == null) {
          MetricServiceGrpc.getListMetricSummariesMethod = getListMetricSummariesMethod =
              io.grpc.MethodDescriptor.<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest, org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listMetricSummaries"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MetricServiceMethodDescriptorSupplier("listMetricSummaries"))
              .build();
        }
      }
    }
    return getListMetricSummariesMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static MetricServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetricServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetricServiceStub>() {
        @java.lang.Override
        public MetricServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetricServiceStub(channel, callOptions);
        }
      };
    return MetricServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static MetricServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetricServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetricServiceBlockingStub>() {
        @java.lang.Override
        public MetricServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetricServiceBlockingStub(channel, callOptions);
        }
      };
    return MetricServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static MetricServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MetricServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MetricServiceFutureStub>() {
        @java.lang.Override
        public MetricServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MetricServiceFutureStub(channel, callOptions);
        }
      };
    return MetricServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public static abstract class MetricServiceImplBase implements io.grpc.BindableService {

    /**
     */
    public void registerMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterMetricMetaMethod(), responseObserver);
    }

    /**
     */
    public void updateMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateMetricMetaMethod(), responseObserver);
    }

    /**
     */
    public void deleteMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteMetricMetaMethod(), responseObserver);
    }

    /**
     */
    public void getMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getGetMetricMetaMethod(), responseObserver);
    }

    /**
     */
    public void listDatasetMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListDatasetMetricMetasMethod(), responseObserver);
    }

    /**
     */
    public void listModelMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListModelMetricMetasMethod(), responseObserver);
    }

    /**
     */
    public void registerMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterMetricSummaryMethod(), responseObserver);
    }

    /**
     */
    public void updateMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateMetricSummaryMethod(), responseObserver);
    }

    /**
     */
    public void deleteMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteMetricSummaryMethod(), responseObserver);
    }

    /**
     */
    public void getMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getGetMetricSummaryMethod(), responseObserver);
    }

    /**
     */
    public void listMetricSummaries(org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListMetricSummariesMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getRegisterMetricMetaMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>(
                  this, METHODID_REGISTER_METRIC_META)))
          .addMethod(
            getUpdateMetricMetaMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>(
                  this, METHODID_UPDATE_METRIC_META)))
          .addMethod(
            getDeleteMetricMetaMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
                org.aiflow.client.proto.Message.Response>(
                  this, METHODID_DELETE_METRIC_META)))
          .addMethod(
            getGetMetricMetaMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>(
                  this, METHODID_GET_METRIC_META)))
          .addMethod(
            getListDatasetMetricMetasMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>(
                  this, METHODID_LIST_DATASET_METRIC_METAS)))
          .addMethod(
            getListModelMetricMetasMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>(
                  this, METHODID_LIST_MODEL_METRIC_METAS)))
          .addMethod(
            getRegisterMetricSummaryMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>(
                  this, METHODID_REGISTER_METRIC_SUMMARY)))
          .addMethod(
            getUpdateMetricSummaryMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>(
                  this, METHODID_UPDATE_METRIC_SUMMARY)))
          .addMethod(
            getDeleteMetricSummaryMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
                org.aiflow.client.proto.Message.Response>(
                  this, METHODID_DELETE_METRIC_SUMMARY)))
          .addMethod(
            getGetMetricSummaryMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>(
                  this, METHODID_GET_METRIC_SUMMARY)))
          .addMethod(
            getListMetricSummariesMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest,
                org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse>(
                  this, METHODID_LIST_METRIC_SUMMARIES)))
          .build();
    }
  }

  /**
   */
  public static final class MetricServiceStub extends io.grpc.stub.AbstractAsyncStub<MetricServiceStub> {
    private MetricServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetricServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetricServiceStub(channel, callOptions);
    }

    /**
     */
    public void registerMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterMetricMetaMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateMetricMetaMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteMetricMetaMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetMetricMetaMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listDatasetMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListDatasetMetricMetasMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listModelMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListModelMetricMetasMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterMetricSummaryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateMetricSummaryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteMetricSummaryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetMetricSummaryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listMetricSummaries(org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest request,
        io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListMetricSummariesMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   */
  public static final class MetricServiceBlockingStub extends io.grpc.stub.AbstractBlockingStub<MetricServiceBlockingStub> {
    private MetricServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetricServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetricServiceBlockingStub(channel, callOptions);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse registerMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterMetricMetaMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse updateMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateMetricMetaMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.Message.Response deleteMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteMetricMetaMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse getMetricMeta(org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetMetricMetaMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse listDatasetMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest request) {
      return blockingUnaryCall(
          getChannel(), getListDatasetMetricMetasMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse listModelMetricMetas(org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest request) {
      return blockingUnaryCall(
          getChannel(), getListModelMetricMetasMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse registerMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterMetricSummaryMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse updateMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateMetricSummaryMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.Message.Response deleteMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteMetricSummaryMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse getMetricSummary(org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetMetricSummaryMethod(), getCallOptions(), request);
    }

    /**
     */
    public org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse listMetricSummaries(org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest request) {
      return blockingUnaryCall(
          getChannel(), getListMetricSummariesMethod(), getCallOptions(), request);
    }
  }

  /**
   */
  public static final class MetricServiceFutureStub extends io.grpc.stub.AbstractFutureStub<MetricServiceFutureStub> {
    private MetricServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MetricServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MetricServiceFutureStub(channel, callOptions);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> registerMetricMeta(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterMetricMetaMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> updateMetricMeta(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateMetricMetaMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.Message.Response> deleteMetricMeta(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteMetricMetaMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse> getMetricMeta(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetMetricMetaMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> listDatasetMetricMetas(
        org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListDatasetMetricMetasMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse> listModelMetricMetas(
        org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListModelMetricMetasMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> registerMetricSummary(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterMetricSummaryMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> updateMetricSummary(
        org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateMetricSummaryMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.Message.Response> deleteMetricSummary(
        org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteMetricSummaryMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse> getMetricSummary(
        org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetMetricSummaryMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse> listMetricSummaries(
        org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListMetricSummariesMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_REGISTER_METRIC_META = 0;
  private static final int METHODID_UPDATE_METRIC_META = 1;
  private static final int METHODID_DELETE_METRIC_META = 2;
  private static final int METHODID_GET_METRIC_META = 3;
  private static final int METHODID_LIST_DATASET_METRIC_METAS = 4;
  private static final int METHODID_LIST_MODEL_METRIC_METAS = 5;
  private static final int METHODID_REGISTER_METRIC_SUMMARY = 6;
  private static final int METHODID_UPDATE_METRIC_SUMMARY = 7;
  private static final int METHODID_DELETE_METRIC_SUMMARY = 8;
  private static final int METHODID_GET_METRIC_SUMMARY = 9;
  private static final int METHODID_LIST_METRIC_SUMMARIES = 10;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final MetricServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(MetricServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_REGISTER_METRIC_META:
          serviceImpl.registerMetricMeta((org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>) responseObserver);
          break;
        case METHODID_UPDATE_METRIC_META:
          serviceImpl.updateMetricMeta((org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>) responseObserver);
          break;
        case METHODID_DELETE_METRIC_META:
          serviceImpl.deleteMetricMeta((org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_METRIC_META:
          serviceImpl.getMetricMeta((org.aiflow.client.proto.MetricServiceOuterClass.MetricNameRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaResponse>) responseObserver);
          break;
        case METHODID_LIST_DATASET_METRIC_METAS:
          serviceImpl.listDatasetMetricMetas((org.aiflow.client.proto.MetricServiceOuterClass.ListDatasetMetricMetasRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>) responseObserver);
          break;
        case METHODID_LIST_MODEL_METRIC_METAS:
          serviceImpl.listModelMetricMetas((org.aiflow.client.proto.MetricServiceOuterClass.ListModelMetricMetasRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricMetasResponse>) responseObserver);
          break;
        case METHODID_REGISTER_METRIC_SUMMARY:
          serviceImpl.registerMetricSummary((org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>) responseObserver);
          break;
        case METHODID_UPDATE_METRIC_SUMMARY:
          serviceImpl.updateMetricSummary((org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>) responseObserver);
          break;
        case METHODID_DELETE_METRIC_SUMMARY:
          serviceImpl.deleteMetricSummary((org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_METRIC_SUMMARY:
          serviceImpl.getMetricSummary((org.aiflow.client.proto.MetricServiceOuterClass.UuidRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryResponse>) responseObserver);
          break;
        case METHODID_LIST_METRIC_SUMMARIES:
          serviceImpl.listMetricSummaries((org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesRequest) request,
              (io.grpc.stub.StreamObserver<org.aiflow.client.proto.MetricServiceOuterClass.ListMetricSummariesResponse>) responseObserver);
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

  private static abstract class MetricServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    MetricServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return org.aiflow.client.proto.MetricServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("MetricService");
    }
  }

  private static final class MetricServiceFileDescriptorSupplier
      extends MetricServiceBaseDescriptorSupplier {
    MetricServiceFileDescriptorSupplier() {}
  }

  private static final class MetricServiceMethodDescriptorSupplier
      extends MetricServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    MetricServiceMethodDescriptorSupplier(String methodName) {
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
      synchronized (MetricServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new MetricServiceFileDescriptorSupplier())
              .addMethod(getRegisterMetricMetaMethod())
              .addMethod(getUpdateMetricMetaMethod())
              .addMethod(getDeleteMetricMetaMethod())
              .addMethod(getGetMetricMetaMethod())
              .addMethod(getListDatasetMetricMetasMethod())
              .addMethod(getListModelMetricMetasMethod())
              .addMethod(getRegisterMetricSummaryMethod())
              .addMethod(getUpdateMetricSummaryMethod())
              .addMethod(getDeleteMetricSummaryMethod())
              .addMethod(getGetMetricSummaryMethod())
              .addMethod(getListMetricSummariesMethod())
              .build();
        }
      }
    }
    return result;
  }
}
