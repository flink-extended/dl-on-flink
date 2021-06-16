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
      com.aiflow.proto.Message.Response> getGetExampleByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getExampleById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetExampleByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetExampleByIdMethod;
    if ((getGetExampleByIdMethod = MetadataServiceGrpc.getGetExampleByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetExampleByIdMethod = MetadataServiceGrpc.getGetExampleByIdMethod) == null) {
          MetadataServiceGrpc.getGetExampleByIdMethod = getGetExampleByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getExampleById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getExampleById"))
              .build();
        }
      }
    }
    return getGetExampleByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetExampleByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getExampleByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetExampleByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetExampleByNameMethod;
    if ((getGetExampleByNameMethod = MetadataServiceGrpc.getGetExampleByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetExampleByNameMethod = MetadataServiceGrpc.getGetExampleByNameMethod) == null) {
          MetadataServiceGrpc.getGetExampleByNameMethod = getGetExampleByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getExampleByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getExampleByName"))
              .build();
        }
      }
    }
    return getGetExampleByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListExampleMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listExample",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListExampleMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListExampleMethod;
    if ((getListExampleMethod = MetadataServiceGrpc.getListExampleMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListExampleMethod = MetadataServiceGrpc.getListExampleMethod) == null) {
          MetadataServiceGrpc.getListExampleMethod = getListExampleMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listExample"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listExample"))
              .build();
        }
      }
    }
    return getListExampleMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
      com.aiflow.proto.Message.Response> getRegisterExampleMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerExample",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
      com.aiflow.proto.Message.Response> getRegisterExampleMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest, com.aiflow.proto.Message.Response> getRegisterExampleMethod;
    if ((getRegisterExampleMethod = MetadataServiceGrpc.getRegisterExampleMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterExampleMethod = MetadataServiceGrpc.getRegisterExampleMethod) == null) {
          MetadataServiceGrpc.getRegisterExampleMethod = getRegisterExampleMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerExample"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerExample"))
              .build();
        }
      }
    }
    return getRegisterExampleMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
      com.aiflow.proto.Message.Response> getRegisterExampleWithCatalogMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerExampleWithCatalog",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
      com.aiflow.proto.Message.Response> getRegisterExampleWithCatalogMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest, com.aiflow.proto.Message.Response> getRegisterExampleWithCatalogMethod;
    if ((getRegisterExampleWithCatalogMethod = MetadataServiceGrpc.getRegisterExampleWithCatalogMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterExampleWithCatalogMethod = MetadataServiceGrpc.getRegisterExampleWithCatalogMethod) == null) {
          MetadataServiceGrpc.getRegisterExampleWithCatalogMethod = getRegisterExampleWithCatalogMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerExampleWithCatalog"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerExampleWithCatalog"))
              .build();
        }
      }
    }
    return getRegisterExampleWithCatalogMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest,
      com.aiflow.proto.Message.Response> getRegisterExamplesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerExamples",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest,
      com.aiflow.proto.Message.Response> getRegisterExamplesMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest, com.aiflow.proto.Message.Response> getRegisterExamplesMethod;
    if ((getRegisterExamplesMethod = MetadataServiceGrpc.getRegisterExamplesMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterExamplesMethod = MetadataServiceGrpc.getRegisterExamplesMethod) == null) {
          MetadataServiceGrpc.getRegisterExamplesMethod = getRegisterExamplesMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerExamples"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerExamples"))
              .build();
        }
      }
    }
    return getRegisterExamplesMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest,
      com.aiflow.proto.Message.Response> getUpdateExampleMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateExample",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest,
      com.aiflow.proto.Message.Response> getUpdateExampleMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest, com.aiflow.proto.Message.Response> getUpdateExampleMethod;
    if ((getUpdateExampleMethod = MetadataServiceGrpc.getUpdateExampleMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateExampleMethod = MetadataServiceGrpc.getUpdateExampleMethod) == null) {
          MetadataServiceGrpc.getUpdateExampleMethod = getUpdateExampleMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateExample"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateExample"))
              .build();
        }
      }
    }
    return getUpdateExampleMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteExampleByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteExampleById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteExampleByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteExampleByIdMethod;
    if ((getDeleteExampleByIdMethod = MetadataServiceGrpc.getDeleteExampleByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteExampleByIdMethod = MetadataServiceGrpc.getDeleteExampleByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteExampleByIdMethod = getDeleteExampleByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteExampleById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteExampleById"))
              .build();
        }
      }
    }
    return getDeleteExampleByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteExampleByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteExampleByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteExampleByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteExampleByNameMethod;
    if ((getDeleteExampleByNameMethod = MetadataServiceGrpc.getDeleteExampleByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteExampleByNameMethod = MetadataServiceGrpc.getDeleteExampleByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteExampleByNameMethod = getDeleteExampleByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteExampleByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteExampleByName"))
              .build();
        }
      }
    }
    return getDeleteExampleByNameMethod;
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
      com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getWorkFlowExecutionById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByIdMethod;
    if ((getGetWorkFlowExecutionByIdMethod = MetadataServiceGrpc.getGetWorkFlowExecutionByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetWorkFlowExecutionByIdMethod = MetadataServiceGrpc.getGetWorkFlowExecutionByIdMethod) == null) {
          MetadataServiceGrpc.getGetWorkFlowExecutionByIdMethod = getGetWorkFlowExecutionByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getWorkFlowExecutionById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getWorkFlowExecutionById"))
              .build();
        }
      }
    }
    return getGetWorkFlowExecutionByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getWorkFlowExecutionByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetWorkFlowExecutionByNameMethod;
    if ((getGetWorkFlowExecutionByNameMethod = MetadataServiceGrpc.getGetWorkFlowExecutionByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetWorkFlowExecutionByNameMethod = MetadataServiceGrpc.getGetWorkFlowExecutionByNameMethod) == null) {
          MetadataServiceGrpc.getGetWorkFlowExecutionByNameMethod = getGetWorkFlowExecutionByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getWorkFlowExecutionByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getWorkFlowExecutionByName"))
              .build();
        }
      }
    }
    return getGetWorkFlowExecutionByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListWorkFlowExecutionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listWorkFlowExecution",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListWorkFlowExecutionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListWorkFlowExecutionMethod;
    if ((getListWorkFlowExecutionMethod = MetadataServiceGrpc.getListWorkFlowExecutionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListWorkFlowExecutionMethod = MetadataServiceGrpc.getListWorkFlowExecutionMethod) == null) {
          MetadataServiceGrpc.getListWorkFlowExecutionMethod = getListWorkFlowExecutionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listWorkFlowExecution"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listWorkFlowExecution"))
              .build();
        }
      }
    }
    return getListWorkFlowExecutionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest,
      com.aiflow.proto.Message.Response> getRegisterWorkFlowExecutionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerWorkFlowExecution",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest,
      com.aiflow.proto.Message.Response> getRegisterWorkFlowExecutionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest, com.aiflow.proto.Message.Response> getRegisterWorkFlowExecutionMethod;
    if ((getRegisterWorkFlowExecutionMethod = MetadataServiceGrpc.getRegisterWorkFlowExecutionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterWorkFlowExecutionMethod = MetadataServiceGrpc.getRegisterWorkFlowExecutionMethod) == null) {
          MetadataServiceGrpc.getRegisterWorkFlowExecutionMethod = getRegisterWorkFlowExecutionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerWorkFlowExecution"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerWorkFlowExecution"))
              .build();
        }
      }
    }
    return getRegisterWorkFlowExecutionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateWorkflowExecution",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest, com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionMethod;
    if ((getUpdateWorkflowExecutionMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateWorkflowExecutionMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionMethod) == null) {
          MetadataServiceGrpc.getUpdateWorkflowExecutionMethod = getUpdateWorkflowExecutionMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateWorkflowExecution"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateWorkflowExecution"))
              .build();
        }
      }
    }
    return getUpdateWorkflowExecutionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteWorkflowExecutionById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByIdMethod;
    if ((getDeleteWorkflowExecutionByIdMethod = MetadataServiceGrpc.getDeleteWorkflowExecutionByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteWorkflowExecutionByIdMethod = MetadataServiceGrpc.getDeleteWorkflowExecutionByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteWorkflowExecutionByIdMethod = getDeleteWorkflowExecutionByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteWorkflowExecutionById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteWorkflowExecutionById"))
              .build();
        }
      }
    }
    return getDeleteWorkflowExecutionByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteWorkflowExecutionByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteWorkflowExecutionByNameMethod;
    if ((getDeleteWorkflowExecutionByNameMethod = MetadataServiceGrpc.getDeleteWorkflowExecutionByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteWorkflowExecutionByNameMethod = MetadataServiceGrpc.getDeleteWorkflowExecutionByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteWorkflowExecutionByNameMethod = getDeleteWorkflowExecutionByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteWorkflowExecutionByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteWorkflowExecutionByName"))
              .build();
        }
      }
    }
    return getDeleteWorkflowExecutionByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionEndTimeMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateWorkflowExecutionEndTime",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionEndTimeMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest, com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionEndTimeMethod;
    if ((getUpdateWorkflowExecutionEndTimeMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionEndTimeMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateWorkflowExecutionEndTimeMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionEndTimeMethod) == null) {
          MetadataServiceGrpc.getUpdateWorkflowExecutionEndTimeMethod = getUpdateWorkflowExecutionEndTimeMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateWorkflowExecutionEndTime"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateWorkflowExecutionEndTime"))
              .build();
        }
      }
    }
    return getUpdateWorkflowExecutionEndTimeMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionStateMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateWorkflowExecutionState",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest,
      com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionStateMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest, com.aiflow.proto.Message.Response> getUpdateWorkflowExecutionStateMethod;
    if ((getUpdateWorkflowExecutionStateMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionStateMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateWorkflowExecutionStateMethod = MetadataServiceGrpc.getUpdateWorkflowExecutionStateMethod) == null) {
          MetadataServiceGrpc.getUpdateWorkflowExecutionStateMethod = getUpdateWorkflowExecutionStateMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateWorkflowExecutionState"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateWorkflowExecutionState"))
              .build();
        }
      }
    }
    return getUpdateWorkflowExecutionStateMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetJobByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getJobById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getGetJobByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getGetJobByIdMethod;
    if ((getGetJobByIdMethod = MetadataServiceGrpc.getGetJobByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetJobByIdMethod = MetadataServiceGrpc.getGetJobByIdMethod) == null) {
          MetadataServiceGrpc.getGetJobByIdMethod = getGetJobByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getJobById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getJobById"))
              .build();
        }
      }
    }
    return getGetJobByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetJobByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "getJobByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getGetJobByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getGetJobByNameMethod;
    if ((getGetJobByNameMethod = MetadataServiceGrpc.getGetJobByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getGetJobByNameMethod = MetadataServiceGrpc.getGetJobByNameMethod) == null) {
          MetadataServiceGrpc.getGetJobByNameMethod = getGetJobByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "getJobByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("getJobByName"))
              .build();
        }
      }
    }
    return getGetJobByNameMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListJobMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listJob",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.ListRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
      com.aiflow.proto.Message.Response> getListJobMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response> getListJobMethod;
    if ((getListJobMethod = MetadataServiceGrpc.getListJobMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getListJobMethod = MetadataServiceGrpc.getListJobMethod) == null) {
          MetadataServiceGrpc.getListJobMethod = getListJobMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.ListRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listJob"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.ListRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("listJob"))
              .build();
        }
      }
    }
    return getListJobMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest,
      com.aiflow.proto.Message.Response> getRegisterJobMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "registerJob",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest,
      com.aiflow.proto.Message.Response> getRegisterJobMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest, com.aiflow.proto.Message.Response> getRegisterJobMethod;
    if ((getRegisterJobMethod = MetadataServiceGrpc.getRegisterJobMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getRegisterJobMethod = MetadataServiceGrpc.getRegisterJobMethod) == null) {
          MetadataServiceGrpc.getRegisterJobMethod = getRegisterJobMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "registerJob"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("registerJob"))
              .build();
        }
      }
    }
    return getRegisterJobMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest,
      com.aiflow.proto.Message.Response> getUpdateJobMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateJob",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest,
      com.aiflow.proto.Message.Response> getUpdateJobMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest, com.aiflow.proto.Message.Response> getUpdateJobMethod;
    if ((getUpdateJobMethod = MetadataServiceGrpc.getUpdateJobMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateJobMethod = MetadataServiceGrpc.getUpdateJobMethod) == null) {
          MetadataServiceGrpc.getUpdateJobMethod = getUpdateJobMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateJob"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateJob"))
              .build();
        }
      }
    }
    return getUpdateJobMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest,
      com.aiflow.proto.Message.Response> getUpdateJobStateMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateJobState",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest,
      com.aiflow.proto.Message.Response> getUpdateJobStateMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest, com.aiflow.proto.Message.Response> getUpdateJobStateMethod;
    if ((getUpdateJobStateMethod = MetadataServiceGrpc.getUpdateJobStateMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateJobStateMethod = MetadataServiceGrpc.getUpdateJobStateMethod) == null) {
          MetadataServiceGrpc.getUpdateJobStateMethod = getUpdateJobStateMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateJobState"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateJobState"))
              .build();
        }
      }
    }
    return getUpdateJobStateMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest,
      com.aiflow.proto.Message.Response> getUpdateJobEndTimeMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "updateJobEndTime",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest,
      com.aiflow.proto.Message.Response> getUpdateJobEndTimeMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest, com.aiflow.proto.Message.Response> getUpdateJobEndTimeMethod;
    if ((getUpdateJobEndTimeMethod = MetadataServiceGrpc.getUpdateJobEndTimeMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getUpdateJobEndTimeMethod = MetadataServiceGrpc.getUpdateJobEndTimeMethod) == null) {
          MetadataServiceGrpc.getUpdateJobEndTimeMethod = getUpdateJobEndTimeMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "updateJobEndTime"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("updateJobEndTime"))
              .build();
        }
      }
    }
    return getUpdateJobEndTimeMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteJobByIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteJobById",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.IdRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
      com.aiflow.proto.Message.Response> getDeleteJobByIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response> getDeleteJobByIdMethod;
    if ((getDeleteJobByIdMethod = MetadataServiceGrpc.getDeleteJobByIdMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteJobByIdMethod = MetadataServiceGrpc.getDeleteJobByIdMethod) == null) {
          MetadataServiceGrpc.getDeleteJobByIdMethod = getDeleteJobByIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.IdRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteJobById"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.IdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteJobById"))
              .build();
        }
      }
    }
    return getDeleteJobByIdMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteJobByNameMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "deleteJobByName",
      requestType = com.aiflow.proto.MetadataServiceOuterClass.NameRequest.class,
      responseType = com.aiflow.proto.Message.Response.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
      com.aiflow.proto.Message.Response> getDeleteJobByNameMethod() {
    io.grpc.MethodDescriptor<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response> getDeleteJobByNameMethod;
    if ((getDeleteJobByNameMethod = MetadataServiceGrpc.getDeleteJobByNameMethod) == null) {
      synchronized (MetadataServiceGrpc.class) {
        if ((getDeleteJobByNameMethod = MetadataServiceGrpc.getDeleteJobByNameMethod) == null) {
          MetadataServiceGrpc.getDeleteJobByNameMethod = getDeleteJobByNameMethod =
              io.grpc.MethodDescriptor.<com.aiflow.proto.MetadataServiceOuterClass.NameRequest, com.aiflow.proto.Message.Response>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "deleteJobByName"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.MetadataServiceOuterClass.NameRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.proto.Message.Response.getDefaultInstance()))
              .setSchemaDescriptor(new MetadataServiceMethodDescriptorSupplier("deleteJobByName"))
              .build();
        }
      }
    }
    return getDeleteJobByNameMethod;
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
     *example api
     * </pre>
     */
    public void getExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetExampleByIdMethod(), responseObserver);
    }

    /**
     */
    public void getExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetExampleByNameMethod(), responseObserver);
    }

    /**
     */
    public void listExample(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListExampleMethod(), responseObserver);
    }

    /**
     */
    public void registerExample(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterExampleMethod(), responseObserver);
    }

    /**
     */
    public void registerExampleWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterExampleWithCatalogMethod(), responseObserver);
    }

    /**
     */
    public void registerExamples(com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterExamplesMethod(), responseObserver);
    }

    /**
     */
    public void updateExample(com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateExampleMethod(), responseObserver);
    }

    /**
     */
    public void deleteExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteExampleByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteExampleByNameMethod(), responseObserver);
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
     *workflow execution api
     * </pre>
     */
    public void getWorkFlowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetWorkFlowExecutionByIdMethod(), responseObserver);
    }

    /**
     */
    public void getWorkFlowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetWorkFlowExecutionByNameMethod(), responseObserver);
    }

    /**
     */
    public void listWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListWorkFlowExecutionMethod(), responseObserver);
    }

    /**
     */
    public void registerWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterWorkFlowExecutionMethod(), responseObserver);
    }

    /**
     */
    public void updateWorkflowExecution(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateWorkflowExecutionMethod(), responseObserver);
    }

    /**
     */
    public void deleteWorkflowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteWorkflowExecutionByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteWorkflowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteWorkflowExecutionByNameMethod(), responseObserver);
    }

    /**
     */
    public void updateWorkflowExecutionEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateWorkflowExecutionEndTimeMethod(), responseObserver);
    }

    /**
     */
    public void updateWorkflowExecutionState(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateWorkflowExecutionStateMethod(), responseObserver);
    }

    /**
     * <pre>
     *job api
     * </pre>
     */
    public void getJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetJobByIdMethod(), responseObserver);
    }

    /**
     */
    public void getJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getGetJobByNameMethod(), responseObserver);
    }

    /**
     */
    public void listJob(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getListJobMethod(), responseObserver);
    }

    /**
     */
    public void registerJob(com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getRegisterJobMethod(), responseObserver);
    }

    /**
     */
    public void updateJob(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateJobMethod(), responseObserver);
    }

    /**
     */
    public void updateJobState(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateJobStateMethod(), responseObserver);
    }

    /**
     */
    public void updateJobEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getUpdateJobEndTimeMethod(), responseObserver);
    }

    /**
     */
    public void deleteJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteJobByIdMethod(), responseObserver);
    }

    /**
     */
    public void deleteJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnimplementedUnaryCall(getDeleteJobByNameMethod(), responseObserver);
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

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getGetExampleByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_EXAMPLE_BY_ID)))
          .addMethod(
            getGetExampleByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_EXAMPLE_BY_NAME)))
          .addMethod(
            getListExampleMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_EXAMPLE)))
          .addMethod(
            getRegisterExampleMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_EXAMPLE)))
          .addMethod(
            getRegisterExampleWithCatalogMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_EXAMPLE_WITH_CATALOG)))
          .addMethod(
            getRegisterExamplesMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_EXAMPLES)))
          .addMethod(
            getUpdateExampleMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_EXAMPLE)))
          .addMethod(
            getDeleteExampleByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_EXAMPLE_BY_ID)))
          .addMethod(
            getDeleteExampleByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_EXAMPLE_BY_NAME)))
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
            getGetWorkFlowExecutionByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_WORK_FLOW_EXECUTION_BY_ID)))
          .addMethod(
            getGetWorkFlowExecutionByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_WORK_FLOW_EXECUTION_BY_NAME)))
          .addMethod(
            getListWorkFlowExecutionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_WORK_FLOW_EXECUTION)))
          .addMethod(
            getRegisterWorkFlowExecutionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_WORK_FLOW_EXECUTION)))
          .addMethod(
            getUpdateWorkflowExecutionMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_WORKFLOW_EXECUTION)))
          .addMethod(
            getDeleteWorkflowExecutionByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_WORKFLOW_EXECUTION_BY_ID)))
          .addMethod(
            getDeleteWorkflowExecutionByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_WORKFLOW_EXECUTION_BY_NAME)))
          .addMethod(
            getUpdateWorkflowExecutionEndTimeMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_WORKFLOW_EXECUTION_END_TIME)))
          .addMethod(
            getUpdateWorkflowExecutionStateMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_WORKFLOW_EXECUTION_STATE)))
          .addMethod(
            getGetJobByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_JOB_BY_ID)))
          .addMethod(
            getGetJobByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_GET_JOB_BY_NAME)))
          .addMethod(
            getListJobMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.ListRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_LIST_JOB)))
          .addMethod(
            getRegisterJobMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_REGISTER_JOB)))
          .addMethod(
            getUpdateJobMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_JOB)))
          .addMethod(
            getUpdateJobStateMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_JOB_STATE)))
          .addMethod(
            getUpdateJobEndTimeMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_UPDATE_JOB_END_TIME)))
          .addMethod(
            getDeleteJobByIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.IdRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_JOB_BY_ID)))
          .addMethod(
            getDeleteJobByNameMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.proto.MetadataServiceOuterClass.NameRequest,
                com.aiflow.proto.Message.Response>(
                  this, METHODID_DELETE_JOB_BY_NAME)))
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
     *example api
     * </pre>
     */
    public void getExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetExampleByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetExampleByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listExample(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListExampleMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerExample(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterExampleMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerExampleWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterExampleWithCatalogMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerExamples(com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterExamplesMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateExample(com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateExampleMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteExampleByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteExampleByNameMethod(), getCallOptions()), request, responseObserver);
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
     *workflow execution api
     * </pre>
     */
    public void getWorkFlowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetWorkFlowExecutionByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getWorkFlowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetWorkFlowExecutionByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListWorkFlowExecutionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterWorkFlowExecutionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateWorkflowExecution(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteWorkflowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteWorkflowExecutionByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteWorkflowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteWorkflowExecutionByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateWorkflowExecutionEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionEndTimeMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateWorkflowExecutionState(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionStateMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     *job api
     * </pre>
     */
    public void getJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetJobByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetJobByNameMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listJob(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListJobMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void registerJob(com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRegisterJobMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateJob(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateJobMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateJobState(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateJobStateMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateJobEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getUpdateJobEndTimeMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteJobByIdMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getDeleteJobByNameMethod(), getCallOptions()), request, responseObserver);
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
     *example api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetExampleByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetExampleByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listExample(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListExampleMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerExample(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterExampleMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerExampleWithCatalog(com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterExampleWithCatalogMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerExamples(com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterExamplesMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateExample(com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateExampleMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteExampleById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteExampleByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteExampleByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteExampleByNameMethod(), getCallOptions(), request);
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
     *workflow execution api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getWorkFlowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetWorkFlowExecutionByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getWorkFlowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetWorkFlowExecutionByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListWorkFlowExecutionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerWorkFlowExecution(com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterWorkFlowExecutionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateWorkflowExecution(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateWorkflowExecutionMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteWorkflowExecutionById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteWorkflowExecutionByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteWorkflowExecutionByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteWorkflowExecutionByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateWorkflowExecutionEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateWorkflowExecutionEndTimeMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateWorkflowExecutionState(com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateWorkflowExecutionStateMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     *job api
     * </pre>
     */
    public com.aiflow.proto.Message.Response getJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetJobByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response getJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetJobByNameMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response listJob(com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return blockingUnaryCall(
          getChannel(), getListJobMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response registerJob(com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest request) {
      return blockingUnaryCall(
          getChannel(), getRegisterJobMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateJob(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateJobMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateJobState(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateJobStateMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response updateJobEndTime(com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest request) {
      return blockingUnaryCall(
          getChannel(), getUpdateJobEndTimeMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteJobById(com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteJobByIdMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.aiflow.proto.Message.Response deleteJobByName(com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return blockingUnaryCall(
          getChannel(), getDeleteJobByNameMethod(), getCallOptions(), request);
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
     *example api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getExampleById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetExampleByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getExampleByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetExampleByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listExample(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListExampleMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerExample(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterExampleMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerExampleWithCatalog(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterExampleWithCatalogMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerExamples(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterExamplesMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateExample(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateExampleMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteExampleById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteExampleByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteExampleByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteExampleByNameMethod(), getCallOptions()), request);
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
     *workflow execution api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getWorkFlowExecutionById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetWorkFlowExecutionByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getWorkFlowExecutionByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetWorkFlowExecutionByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listWorkFlowExecution(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListWorkFlowExecutionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerWorkFlowExecution(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterWorkFlowExecutionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateWorkflowExecution(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteWorkflowExecutionById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteWorkflowExecutionByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteWorkflowExecutionByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteWorkflowExecutionByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateWorkflowExecutionEndTime(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionEndTimeMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateWorkflowExecutionState(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateWorkflowExecutionStateMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     *job api
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getJobById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetJobByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> getJobByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetJobByNameMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> listJob(
        com.aiflow.proto.MetadataServiceOuterClass.ListRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListJobMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> registerJob(
        com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRegisterJobMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateJob(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateJobMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateJobState(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateJobStateMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> updateJobEndTime(
        com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getUpdateJobEndTimeMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteJobById(
        com.aiflow.proto.MetadataServiceOuterClass.IdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteJobByIdMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.proto.Message.Response> deleteJobByName(
        com.aiflow.proto.MetadataServiceOuterClass.NameRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getDeleteJobByNameMethod(), getCallOptions()), request);
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
  }

  private static final int METHODID_GET_EXAMPLE_BY_ID = 0;
  private static final int METHODID_GET_EXAMPLE_BY_NAME = 1;
  private static final int METHODID_LIST_EXAMPLE = 2;
  private static final int METHODID_REGISTER_EXAMPLE = 3;
  private static final int METHODID_REGISTER_EXAMPLE_WITH_CATALOG = 4;
  private static final int METHODID_REGISTER_EXAMPLES = 5;
  private static final int METHODID_UPDATE_EXAMPLE = 6;
  private static final int METHODID_DELETE_EXAMPLE_BY_ID = 7;
  private static final int METHODID_DELETE_EXAMPLE_BY_NAME = 8;
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
  private static final int METHODID_GET_WORK_FLOW_EXECUTION_BY_ID = 30;
  private static final int METHODID_GET_WORK_FLOW_EXECUTION_BY_NAME = 31;
  private static final int METHODID_LIST_WORK_FLOW_EXECUTION = 32;
  private static final int METHODID_REGISTER_WORK_FLOW_EXECUTION = 33;
  private static final int METHODID_UPDATE_WORKFLOW_EXECUTION = 34;
  private static final int METHODID_DELETE_WORKFLOW_EXECUTION_BY_ID = 35;
  private static final int METHODID_DELETE_WORKFLOW_EXECUTION_BY_NAME = 36;
  private static final int METHODID_UPDATE_WORKFLOW_EXECUTION_END_TIME = 37;
  private static final int METHODID_UPDATE_WORKFLOW_EXECUTION_STATE = 38;
  private static final int METHODID_GET_JOB_BY_ID = 39;
  private static final int METHODID_GET_JOB_BY_NAME = 40;
  private static final int METHODID_LIST_JOB = 41;
  private static final int METHODID_REGISTER_JOB = 42;
  private static final int METHODID_UPDATE_JOB = 43;
  private static final int METHODID_UPDATE_JOB_STATE = 44;
  private static final int METHODID_UPDATE_JOB_END_TIME = 45;
  private static final int METHODID_DELETE_JOB_BY_ID = 46;
  private static final int METHODID_DELETE_JOB_BY_NAME = 47;
  private static final int METHODID_GET_PROJECT_BY_ID = 48;
  private static final int METHODID_GET_PROJECT_BY_NAME = 49;
  private static final int METHODID_REGISTER_PROJECT = 50;
  private static final int METHODID_UPDATE_PROJECT = 51;
  private static final int METHODID_LIST_PROJECT = 52;
  private static final int METHODID_DELETE_PROJECT_BY_ID = 53;
  private static final int METHODID_DELETE_PROJECT_BY_NAME = 54;
  private static final int METHODID_GET_ARTIFACT_BY_ID = 55;
  private static final int METHODID_GET_ARTIFACT_BY_NAME = 56;
  private static final int METHODID_UPDATE_ARTIFACT = 57;
  private static final int METHODID_REGISTER_ARTIFACT = 58;
  private static final int METHODID_LIST_ARTIFACT = 59;
  private static final int METHODID_DELETE_ARTIFACT_BY_ID = 60;
  private static final int METHODID_DELETE_ARTIFACT_BY_NAME = 61;

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
        case METHODID_GET_EXAMPLE_BY_ID:
          serviceImpl.getExampleById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_EXAMPLE_BY_NAME:
          serviceImpl.getExampleByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_EXAMPLE:
          serviceImpl.listExample((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_EXAMPLE:
          serviceImpl.registerExample((com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_EXAMPLE_WITH_CATALOG:
          serviceImpl.registerExampleWithCatalog((com.aiflow.proto.MetadataServiceOuterClass.RegisterExampleRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_EXAMPLES:
          serviceImpl.registerExamples((com.aiflow.proto.MetadataServiceOuterClass.RegisterExamplesRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_EXAMPLE:
          serviceImpl.updateExample((com.aiflow.proto.MetadataServiceOuterClass.UpdateExampleRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_EXAMPLE_BY_ID:
          serviceImpl.deleteExampleById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_EXAMPLE_BY_NAME:
          serviceImpl.deleteExampleByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
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
        case METHODID_GET_WORK_FLOW_EXECUTION_BY_ID:
          serviceImpl.getWorkFlowExecutionById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_WORK_FLOW_EXECUTION_BY_NAME:
          serviceImpl.getWorkFlowExecutionByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_WORK_FLOW_EXECUTION:
          serviceImpl.listWorkFlowExecution((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_WORK_FLOW_EXECUTION:
          serviceImpl.registerWorkFlowExecution((com.aiflow.proto.MetadataServiceOuterClass.RegisterWorkFlowExecutionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_WORKFLOW_EXECUTION:
          serviceImpl.updateWorkflowExecution((com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_WORKFLOW_EXECUTION_BY_ID:
          serviceImpl.deleteWorkflowExecutionById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_WORKFLOW_EXECUTION_BY_NAME:
          serviceImpl.deleteWorkflowExecutionByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_WORKFLOW_EXECUTION_END_TIME:
          serviceImpl.updateWorkflowExecutionEndTime((com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionEndTimeRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_WORKFLOW_EXECUTION_STATE:
          serviceImpl.updateWorkflowExecutionState((com.aiflow.proto.MetadataServiceOuterClass.UpdateWorkflowExecutionStateRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_JOB_BY_ID:
          serviceImpl.getJobById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_GET_JOB_BY_NAME:
          serviceImpl.getJobByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_LIST_JOB:
          serviceImpl.listJob((com.aiflow.proto.MetadataServiceOuterClass.ListRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_REGISTER_JOB:
          serviceImpl.registerJob((com.aiflow.proto.MetadataServiceOuterClass.RegisterJobRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_JOB:
          serviceImpl.updateJob((com.aiflow.proto.MetadataServiceOuterClass.UpdateJobRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_JOB_STATE:
          serviceImpl.updateJobState((com.aiflow.proto.MetadataServiceOuterClass.UpdateJobStateRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_UPDATE_JOB_END_TIME:
          serviceImpl.updateJobEndTime((com.aiflow.proto.MetadataServiceOuterClass.UpdateJobEndTimeRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_JOB_BY_ID:
          serviceImpl.deleteJobById((com.aiflow.proto.MetadataServiceOuterClass.IdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.proto.Message.Response>) responseObserver);
          break;
        case METHODID_DELETE_JOB_BY_NAME:
          serviceImpl.deleteJobByName((com.aiflow.proto.MetadataServiceOuterClass.NameRequest) request,
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
              .addMethod(getGetExampleByIdMethod())
              .addMethod(getGetExampleByNameMethod())
              .addMethod(getListExampleMethod())
              .addMethod(getRegisterExampleMethod())
              .addMethod(getRegisterExampleWithCatalogMethod())
              .addMethod(getRegisterExamplesMethod())
              .addMethod(getUpdateExampleMethod())
              .addMethod(getDeleteExampleByIdMethod())
              .addMethod(getDeleteExampleByNameMethod())
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
              .addMethod(getGetWorkFlowExecutionByIdMethod())
              .addMethod(getGetWorkFlowExecutionByNameMethod())
              .addMethod(getListWorkFlowExecutionMethod())
              .addMethod(getRegisterWorkFlowExecutionMethod())
              .addMethod(getUpdateWorkflowExecutionMethod())
              .addMethod(getDeleteWorkflowExecutionByIdMethod())
              .addMethod(getDeleteWorkflowExecutionByNameMethod())
              .addMethod(getUpdateWorkflowExecutionEndTimeMethod())
              .addMethod(getUpdateWorkflowExecutionStateMethod())
              .addMethod(getGetJobByIdMethod())
              .addMethod(getGetJobByNameMethod())
              .addMethod(getListJobMethod())
              .addMethod(getRegisterJobMethod())
              .addMethod(getUpdateJobMethod())
              .addMethod(getUpdateJobStateMethod())
              .addMethod(getUpdateJobEndTimeMethod())
              .addMethod(getDeleteJobByIdMethod())
              .addMethod(getDeleteJobByNameMethod())
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
              .build();
        }
      }
    }
    return result;
  }
}
