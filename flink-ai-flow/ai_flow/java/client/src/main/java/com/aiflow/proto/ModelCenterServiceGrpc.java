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
 * <pre>
 * AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
 * Functions of ModelCenterService include:
 *  1.Create registered model
 *  2.Update registered model
 *  3.Delete registered model
 *  4.List registered models
 *  5.Get registered model detail
 *  6.Create model version
 *  7.Update model version
 *  8.Delete model version
 *  9.Get model version detail
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.29.0-SNAPSHOT)",
    comments = "Source: model_center_service.proto")
public final class ModelCenterServiceGrpc {

  private ModelCenterServiceGrpc() {}

  public static final String SERVICE_NAME = "ai_flow.ModelCenterService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getCreateRegisteredModelMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "createRegisteredModel",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getCreateRegisteredModelMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest, com.aiflow.proto.Message.Response> getCreateRegisteredModelMethod;
    if ((getCreateRegisteredModelMethod = ModelCenterServiceGrpc.getCreateRegisteredModelMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getCreateRegisteredModelMethod = ModelCenterServiceGrpc.getCreateRegisteredModelMethod) == null) {
          ModelCenterServiceGrpc.getCreateRegisteredModelMethod = getCreateRegisteredModelMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "createRegisteredModel"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("createRegisteredModel"))
              .build();
        }
      }
    }
    return getCreateRegisteredModelMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getUpdateRegisteredModelMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateRegisteredModel",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getUpdateRegisteredModelMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest, com.aiflow.proto.Message.Response> getUpdateRegisteredModelMethod;
    if ((getUpdateRegisteredModelMethod = ModelCenterServiceGrpc.getUpdateRegisteredModelMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getUpdateRegisteredModelMethod = ModelCenterServiceGrpc.getUpdateRegisteredModelMethod) == null) {
          ModelCenterServiceGrpc.getUpdateRegisteredModelMethod = getUpdateRegisteredModelMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateRegisteredModel"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("updateRegisteredModel"))
              .build();
        }
      }
    }
    return getUpdateRegisteredModelMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getDeleteRegisteredModelMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteRegisteredModel",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest,
      com.aiflow.proto.Message.Response> getDeleteRegisteredModelMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest, com.aiflow.proto.Message.Response> getDeleteRegisteredModelMethod;
    if ((getDeleteRegisteredModelMethod = ModelCenterServiceGrpc.getDeleteRegisteredModelMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getDeleteRegisteredModelMethod = ModelCenterServiceGrpc.getDeleteRegisteredModelMethod) == null) {
          ModelCenterServiceGrpc.getDeleteRegisteredModelMethod = getDeleteRegisteredModelMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteRegisteredModel"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("deleteRegisteredModel"))
              .build();
        }
      }
    }
    return getDeleteRegisteredModelMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest,
      com.aiflow.proto.Message.Response> getListRegisteredModelsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listRegisteredModels",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest,
      com.aiflow.proto.Message.Response> getListRegisteredModelsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest, com.aiflow.proto.Message.Response> getListRegisteredModelsMethod;
    if ((getListRegisteredModelsMethod = ModelCenterServiceGrpc.getListRegisteredModelsMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getListRegisteredModelsMethod = ModelCenterServiceGrpc.getListRegisteredModelsMethod) == null) {
          ModelCenterServiceGrpc.getListRegisteredModelsMethod = getListRegisteredModelsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listRegisteredModels"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("listRegisteredModels"))
              .build();
        }
      }
    }
    return getListRegisteredModelsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest,
      com.aiflow.proto.Message.Response> getGetRegisteredModelDetailMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getRegisteredModelDetail",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest,
      com.aiflow.proto.Message.Response> getGetRegisteredModelDetailMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest, com.aiflow.proto.Message.Response> getGetRegisteredModelDetailMethod;
    if ((getGetRegisteredModelDetailMethod = ModelCenterServiceGrpc.getGetRegisteredModelDetailMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getGetRegisteredModelDetailMethod = ModelCenterServiceGrpc.getGetRegisteredModelDetailMethod) == null) {
          ModelCenterServiceGrpc.getGetRegisteredModelDetailMethod = getGetRegisteredModelDetailMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getRegisteredModelDetail"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("getRegisteredModelDetail"))
              .build();
        }
      }
    }
    return getGetRegisteredModelDetailMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest,
      com.aiflow.proto.Message.Response> getCreateModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "createModelVersion",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest,
      com.aiflow.proto.Message.Response> getCreateModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest, com.aiflow.proto.Message.Response> getCreateModelVersionMethod;
    if ((getCreateModelVersionMethod = ModelCenterServiceGrpc.getCreateModelVersionMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getCreateModelVersionMethod = ModelCenterServiceGrpc.getCreateModelVersionMethod) == null) {
          ModelCenterServiceGrpc.getCreateModelVersionMethod = getCreateModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "createModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("createModelVersion"))
              .build();
        }
      }
    }
    return getCreateModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest,
      com.aiflow.proto.Message.Response> getUpdateModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateModelVersion",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest,
      com.aiflow.proto.Message.Response> getUpdateModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest, com.aiflow.proto.Message.Response> getUpdateModelVersionMethod;
    if ((getUpdateModelVersionMethod = ModelCenterServiceGrpc.getUpdateModelVersionMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getUpdateModelVersionMethod = ModelCenterServiceGrpc.getUpdateModelVersionMethod) == null) {
          ModelCenterServiceGrpc.getUpdateModelVersionMethod = getUpdateModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("updateModelVersion"))
              .build();
        }
      }
    }
    return getUpdateModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteModelVersion",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest,
      com.aiflow.proto.Message.Response> getDeleteModelVersionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest, com.aiflow.proto.Message.Response> getDeleteModelVersionMethod;
    if ((getDeleteModelVersionMethod = ModelCenterServiceGrpc.getDeleteModelVersionMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getDeleteModelVersionMethod = ModelCenterServiceGrpc.getDeleteModelVersionMethod) == null) {
          ModelCenterServiceGrpc.getDeleteModelVersionMethod = getDeleteModelVersionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteModelVersion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("deleteModelVersion"))
              .build();
        }
      }
    }
    return getDeleteModelVersionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionDetailMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getModelVersionDetail",
      requestType = com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest,
      com.aiflow.proto.Message.Response> getGetModelVersionDetailMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest, com.aiflow.proto.Message.Response> getGetModelVersionDetailMethod;
    if ((getGetModelVersionDetailMethod = ModelCenterServiceGrpc.getGetModelVersionDetailMethod) == null) {
      synchronized (ModelCenterServiceGrpc.class) {
        if ((getGetModelVersionDetailMethod = ModelCenterServiceGrpc.getGetModelVersionDetailMethod) == null) {
          ModelCenterServiceGrpc.getGetModelVersionDetailMethod = getGetModelVersionDetailMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getModelVersionDetail"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new ModelCenterServiceMethodDescriptorSupplier("getModelVersionDetail"))
              .build();
        }
      }
    }
    return getGetModelVersionDetailMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static ModelCenterServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceStub>() {
        @java.lang.Override
        public ModelCenterServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ModelCenterServiceStub(channel, callOptions);
        }
      };
    return ModelCenterServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static ModelCenterServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceBlockingStub>() {
        @java.lang.Override
        public ModelCenterServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ModelCenterServiceBlockingStub(channel, callOptions);
        }
      };
    return ModelCenterServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static ModelCenterServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ModelCenterServiceFutureStub>() {
        @java.lang.Override
        public ModelCenterServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ModelCenterServiceFutureStub(channel, callOptions);
        }
      };
    return ModelCenterServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
   * Functions of ModelCenterService include:
   *  1.Create registered model
   *  2.Update registered model
   *  3.Delete registered model
   *  4.List registered models
   *  5.Get registered model detail
   *  6.Create model version
   *  7.Update model version
   *  8.Delete model version
   *  9.Get model version detail
   * </pre>
   */
  public static abstract class ModelCenterServiceImplBase implements io.grpc.BindableService {

    /**
     * <pre>
     * Create registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void createRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getCreateRegisteredModelMethod(), responseObserver);
    }

    /**
     * <pre>
     * Update registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void updateRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateRegisteredModelMethod(), responseObserver);
    }

    /**
     * <pre>
     * Delete registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void deleteRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteRegisteredModelMethod(), responseObserver);
    }

    /**
     * <pre>
     * List registered models about metadata of RegisteredModel.
     * </pre>
     */
    public void listRegisteredModels(com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListRegisteredModelsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Get registered model detail including metadata of RegisteredModel.
     * </pre>
     */
    public void getRegisteredModelDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetRegisteredModelDetailMethod(), responseObserver);
    }

    /**
     * <pre>
     * Create model version with metadata of ModelVersion.
     * </pre>
     */
    public void createModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getCreateModelVersionMethod(), responseObserver);
    }

    /**
     * <pre>
     * Update model version with metadata of ModelVersion.
     * </pre>
     */
    public void updateModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateModelVersionMethod(), responseObserver);
    }

    /**
     * <pre>
     * Delete model version with metadata of ModelVersion.
     * </pre>
     */
    public void deleteModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteModelVersionMethod(), responseObserver);
    }

    /**
     * <pre>
     * Get model version detail with metadata of ModelVersion.
     * </pre>
     */
    public void getModelVersionDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetModelVersionDetailMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getCreateRegisteredModelMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_CREATE_REGISTERED_MODEL)))
          .addMethod(
            getUpdateRegisteredModelMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_REGISTERED_MODEL)))
          .addMethod(
            getDeleteRegisteredModelMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_REGISTERED_MODEL)))
          .addMethod(
            getListRegisteredModelsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_REGISTERED_MODELS)))
          .addMethod(
            getGetRegisteredModelDetailMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_REGISTERED_MODEL_DETAIL)))
          .addMethod(
            getCreateModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_CREATE_MODEL_VERSION)))
          .addMethod(
            getUpdateModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_MODEL_VERSION)))
          .addMethod(
            getDeleteModelVersionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_MODEL_VERSION)))
          .addMethod(
            getGetModelVersionDetailMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_MODEL_VERSION_DETAIL)))
          .build();
    }
  }

  /**
   * <pre>
   * AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
   * Functions of ModelCenterService include:
   *  1.Create registered model
   *  2.Update registered model
   *  3.Delete registered model
   *  4.List registered models
   *  5.Get registered model detail
   *  6.Create model version
   *  7.Update model version
   *  8.Delete model version
   *  9.Get model version detail
   * </pre>
   */
  public static final class ModelCenterServiceStub extends io.grpc.stub.AbstractAsyncStub<ModelCenterServiceStub> {
    private ModelCenterServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ModelCenterServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ModelCenterServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Create registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void createRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getCreateRegisteredModelMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Update registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void updateRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateRegisteredModelMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Delete registered model with metadata of RegisteredModel.
     * </pre>
     */
    public void deleteRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteRegisteredModelMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * List registered models about metadata of RegisteredModel.
     * </pre>
     */
    public void listRegisteredModels(com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListRegisteredModelsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Get registered model detail including metadata of RegisteredModel.
     * </pre>
     */
    public void getRegisteredModelDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetRegisteredModelDetailMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Create model version with metadata of ModelVersion.
     * </pre>
     */
    public void createModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getCreateModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Update model version with metadata of ModelVersion.
     * </pre>
     */
    public void updateModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Delete model version with metadata of ModelVersion.
     * </pre>
     */
    public void deleteModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteModelVersionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Get model version detail with metadata of ModelVersion.
     * </pre>
     */
    public void getModelVersionDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetModelVersionDetailMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * <pre>
   * AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
   * Functions of ModelCenterService include:
   *  1.Create registered model
   *  2.Update registered model
   *  3.Delete registered model
   *  4.List registered models
   *  5.Get registered model detail
   *  6.Create model version
   *  7.Update model version
   *  8.Delete model version
   *  9.Get model version detail
   * </pre>
   */
  public static final class ModelCenterServiceBlockingStub extends io.grpc.stub.AbstractBlockingStub<ModelCenterServiceBlockingStub> {
    private ModelCenterServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ModelCenterServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ModelCenterServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Create registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.aiflow.proto.Message.Response createRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest request) {
      return blockingUnaryCall(
          getChannel(), getCreateRegisteredModelMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Update registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.aiflow.proto.Message.Response updateRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateRegisteredModelMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Delete registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.aiflow.proto.Message.Response deleteRegisteredModel(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteRegisteredModelMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * List registered models about metadata of RegisteredModel.
     * </pre>
     */
    public com.aiflow.proto.Message.Response listRegisteredModels(com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest request) {
      return blockingUnaryCall(
          getChannel(), getListRegisteredModelsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Get registered model detail including metadata of RegisteredModel.
     * </pre>
     */
    public com.aiflow.proto.Message.Response getRegisteredModelDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetRegisteredModelDetailMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Create model version with metadata of ModelVersion.
     * </pre>
     */
    public com.aiflow.proto.Message.Response createModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest request) {
      return blockingUnaryCall(
          getChannel(), getCreateModelVersionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Update model version with metadata of ModelVersion.
     * </pre>
     */
    public com.aiflow.proto.Message.Response updateModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateModelVersionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Delete model version with metadata of ModelVersion.
     * </pre>
     */
    public com.aiflow.proto.Message.Response deleteModelVersion(com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteModelVersionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Get model version detail with metadata of ModelVersion.
     * </pre>
     */
    public com.aiflow.proto.Message.Response getModelVersionDetail(com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetModelVersionDetailMethod(), getCallOptions(), request);
    }
  }

  /**
   * <pre>
   * AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
   * Functions of ModelCenterService include:
   *  1.Create registered model
   *  2.Update registered model
   *  3.Delete registered model
   *  4.List registered models
   *  5.Get registered model detail
   *  6.Create model version
   *  7.Update model version
   *  8.Delete model version
   *  9.Get model version detail
   * </pre>
   */
  public static final class ModelCenterServiceFutureStub extends io.grpc.stub.AbstractFutureStub<ModelCenterServiceFutureStub> {
    private ModelCenterServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ModelCenterServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ModelCenterServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Create registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> createRegisteredModel(
        com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getCreateRegisteredModelMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Update registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateRegisteredModel(
        com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateRegisteredModelMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Delete registered model with metadata of RegisteredModel.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteRegisteredModel(
        com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteRegisteredModelMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * List registered models about metadata of RegisteredModel.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listRegisteredModels(
        com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListRegisteredModelsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Get registered model detail including metadata of RegisteredModel.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getRegisteredModelDetail(
        com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetRegisteredModelDetailMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Create model version with metadata of ModelVersion.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> createModelVersion(
        com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getCreateModelVersionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Update model version with metadata of ModelVersion.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateModelVersion(
        com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateModelVersionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Delete model version with metadata of ModelVersion.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteModelVersion(
        com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteModelVersionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Get model version detail with metadata of ModelVersion.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getModelVersionDetail(
        com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetModelVersionDetailMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_CREATE_REGISTERED_MODEL = 0;
  private static final int METHODID_UPDATE_REGISTERED_MODEL = 1;
  private static final int METHODID_DELETE_REGISTERED_MODEL = 2;
  private static final int METHODID_LIST_REGISTERED_MODELS = 3;
  private static final int METHODID_GET_REGISTERED_MODEL_DETAIL = 4;
  private static final int METHODID_CREATE_MODEL_VERSION = 5;
  private static final int METHODID_UPDATE_MODEL_VERSION = 6;
  private static final int METHODID_DELETE_MODEL_VERSION = 7;
  private static final int METHODID_GET_MODEL_VERSION_DETAIL = 8;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final ModelCenterServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(ModelCenterServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_CREATE_REGISTERED_MODEL:
          serviceImpl.createRegisteredModel((com.aiflow.proto.ModelCenterServiceOuterClass.CreateRegisteredModelRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_REGISTERED_MODEL:
          serviceImpl.updateRegisteredModel((com.aiflow.proto.ModelCenterServiceOuterClass.UpdateRegisteredModelRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_REGISTERED_MODEL:
          serviceImpl.deleteRegisteredModel((com.aiflow.proto.ModelCenterServiceOuterClass.DeleteRegisteredModelRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_REGISTERED_MODELS:
          serviceImpl.listRegisteredModels((com.aiflow.proto.ModelCenterServiceOuterClass.ListRegisteredModelsRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_REGISTERED_MODEL_DETAIL:
          serviceImpl.getRegisteredModelDetail((com.aiflow.proto.ModelCenterServiceOuterClass.GetRegisteredModelDetailRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_CREATE_MODEL_VERSION:
          serviceImpl.createModelVersion((com.aiflow.proto.ModelCenterServiceOuterClass.CreateModelVersionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_MODEL_VERSION:
          serviceImpl.updateModelVersion((com.aiflow.proto.ModelCenterServiceOuterClass.UpdateModelVersionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_MODEL_VERSION:
          serviceImpl.deleteModelVersion((com.aiflow.proto.ModelCenterServiceOuterClass.DeleteModelVersionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_MODEL_VERSION_DETAIL:
          serviceImpl.getModelVersionDetail((com.aiflow.proto.ModelCenterServiceOuterClass.GetModelVersionDetailRequest) request,
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

  private static abstract class ModelCenterServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    ModelCenterServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.aiflow.proto.ModelCenterServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("ModelCenterService");
    }
  }

  private static final class ModelCenterServiceFileDescriptorSupplier
      extends ModelCenterServiceBaseDescriptorSupplier {
    ModelCenterServiceFileDescriptorSupplier() {}
  }

  private static final class ModelCenterServiceMethodDescriptorSupplier
      extends ModelCenterServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    ModelCenterServiceMethodDescriptorSupplier(String methodName) {
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
      synchronized (ModelCenterServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new ModelCenterServiceFileDescriptorSupplier())
              .addMethod(getCreateRegisteredModelMethod())
              .addMethod(getUpdateRegisteredModelMethod())
              .addMethod(getDeleteRegisteredModelMethod())
              .addMethod(getListRegisteredModelsMethod())
              .addMethod(getGetRegisteredModelDetailMethod())
              .addMethod(getCreateModelVersionMethod())
              .addMethod(getUpdateModelVersionMethod())
              .addMethod(getDeleteModelVersionMethod())
              .addMethod(getGetModelVersionDetailMethod())
              .build();
        }
      }
    }
    return result;
  }
}
