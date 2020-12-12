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
package com.aiflow.notification.proto;

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
 * AirFlowService provides notification function rest endpoint of NotificationService for Notification Service component.
 * Functions of NotificationService include:
 *  1.Send event.
 *  2.List events.
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.29.0-SNAPSHOT)",
    comments = "Source: notification_service.proto")
public final class NotificationServiceGrpc {

  private NotificationServiceGrpc() {}

  public static final String SERVICE_NAME = "notification_service.NotificationService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> getSendEventMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "sendEvent",
      requestType = com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest.class,
      responseType = com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> getSendEventMethod() {
    io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> getSendEventMethod;
    if ((getSendEventMethod = NotificationServiceGrpc.getSendEventMethod) == null) {
      synchronized (NotificationServiceGrpc.class) {
        if ((getSendEventMethod = NotificationServiceGrpc.getSendEventMethod) == null) {
          NotificationServiceGrpc.getSendEventMethod = getSendEventMethod =
              io.grpc.MethodDescriptor.<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "sendEvent"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new NotificationServiceMethodDescriptorSupplier("sendEvent"))
              .build();
        }
      }
    }
    return getSendEventMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listEvents",
      requestType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest.class,
      responseType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsMethod;
    if ((getListEventsMethod = NotificationServiceGrpc.getListEventsMethod) == null) {
      synchronized (NotificationServiceGrpc.class) {
        if ((getListEventsMethod = NotificationServiceGrpc.getListEventsMethod) == null) {
          NotificationServiceGrpc.getListEventsMethod = getListEventsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new NotificationServiceMethodDescriptorSupplier("listEvents"))
              .build();
        }
      }
    }
    return getListEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListAllEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listAllEvents",
      requestType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest.class,
      responseType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListAllEventsMethod() {
    io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListAllEventsMethod;
    if ((getListAllEventsMethod = NotificationServiceGrpc.getListAllEventsMethod) == null) {
      synchronized (NotificationServiceGrpc.class) {
        if ((getListAllEventsMethod = NotificationServiceGrpc.getListAllEventsMethod) == null) {
          NotificationServiceGrpc.getListAllEventsMethod = getListAllEventsMethod =
              io.grpc.MethodDescriptor.<com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listAllEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new NotificationServiceMethodDescriptorSupplier("listAllEvents"))
              .build();
        }
      }
    }
    return getListAllEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsFromIdMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "listEventsFromId",
      requestType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest.class,
      responseType = com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest,
      com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsFromIdMethod() {
    io.grpc.MethodDescriptor<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> getListEventsFromIdMethod;
    if ((getListEventsFromIdMethod = NotificationServiceGrpc.getListEventsFromIdMethod) == null) {
      synchronized (NotificationServiceGrpc.class) {
        if ((getListEventsFromIdMethod = NotificationServiceGrpc.getListEventsFromIdMethod) == null) {
          NotificationServiceGrpc.getListEventsFromIdMethod = getListEventsFromIdMethod =
              io.grpc.MethodDescriptor.<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest, com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "listEventsFromId"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new NotificationServiceMethodDescriptorSupplier("listEventsFromId"))
              .build();
        }
      }
    }
    return getListEventsFromIdMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static NotificationServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<NotificationServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<NotificationServiceStub>() {
        @java.lang.Override
        public NotificationServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new NotificationServiceStub(channel, callOptions);
        }
      };
    return NotificationServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static NotificationServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<NotificationServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<NotificationServiceBlockingStub>() {
        @java.lang.Override
        public NotificationServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new NotificationServiceBlockingStub(channel, callOptions);
        }
      };
    return NotificationServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static NotificationServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<NotificationServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<NotificationServiceFutureStub>() {
        @java.lang.Override
        public NotificationServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new NotificationServiceFutureStub(channel, callOptions);
        }
      };
    return NotificationServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * AirFlowService provides notification function rest endpoint of NotificationService for Notification Service component.
   * Functions of NotificationService include:
   *  1.Send event.
   *  2.List events.
   * </pre>
   */
  public static abstract class NotificationServiceImplBase implements io.grpc.BindableService {

    /**
     * <pre>
     * Send event.
     * </pre>
     */
    public void sendEvent(com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getSendEventMethod(), responseObserver);
    }

    /**
     * <pre>
     * List events.
     * </pre>
     */
    public void listEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * List all events from the start time.
     * </pre>
     */
    public void listAllEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListAllEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * List all events from the id.
     * </pre>
     */
    public void listEventsFromId(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getListEventsFromIdMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getSendEventMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest,
                com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse>(
                  this, METHODID_SEND_EVENT)))
          .addMethod(
            getListEventsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest,
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>(
                  this, METHODID_LIST_EVENTS)))
          .addMethod(
            getListAllEventsMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest,
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>(
                  this, METHODID_LIST_ALL_EVENTS)))
          .addMethod(
            getListEventsFromIdMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest,
                com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>(
                  this, METHODID_LIST_EVENTS_FROM_ID)))
          .build();
    }
  }

  /**
   * <pre>
   * AirFlowService provides notification function rest endpoint of NotificationService for Notification Service component.
   * Functions of NotificationService include:
   *  1.Send event.
   *  2.List events.
   * </pre>
   */
  public static final class NotificationServiceStub extends io.grpc.stub.AbstractAsyncStub<NotificationServiceStub> {
    private NotificationServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected NotificationServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new NotificationServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Send event.
     * </pre>
     */
    public void sendEvent(com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getSendEventMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * List events.
     * </pre>
     */
    public void listEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * List all events from the start time.
     * </pre>
     */
    public void listAllEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListAllEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * List all events from the id.
     * </pre>
     */
    public void listEventsFromId(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest request,
        io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getListEventsFromIdMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * <pre>
   * AirFlowService provides notification function rest endpoint of NotificationService for Notification Service component.
   * Functions of NotificationService include:
   *  1.Send event.
   *  2.List events.
   * </pre>
   */
  public static final class NotificationServiceBlockingStub extends io.grpc.stub.AbstractBlockingStub<NotificationServiceBlockingStub> {
    private NotificationServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected NotificationServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new NotificationServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Send event.
     * </pre>
     */
    public com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse sendEvent(com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest request) {
      return blockingUnaryCall(
          getChannel(), getSendEventMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * List events.
     * </pre>
     */
    public com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse listEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest request) {
      return blockingUnaryCall(
          getChannel(), getListEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * List all events from the start time.
     * </pre>
     */
    public com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse listAllEvents(com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest request) {
      return blockingUnaryCall(
          getChannel(), getListAllEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * List all events from the id.
     * </pre>
     */
    public com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse listEventsFromId(com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest request) {
      return blockingUnaryCall(
          getChannel(), getListEventsFromIdMethod(), getCallOptions(), request);
    }
  }

  /**
   * <pre>
   * AirFlowService provides notification function rest endpoint of NotificationService for Notification Service component.
   * Functions of NotificationService include:
   *  1.Send event.
   *  2.List events.
   * </pre>
   */
  public static final class NotificationServiceFutureStub extends io.grpc.stub.AbstractFutureStub<NotificationServiceFutureStub> {
    private NotificationServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected NotificationServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new NotificationServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Send event.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse> sendEvent(
        com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getSendEventMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * List events.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> listEvents(
        com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListEventsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * List all events from the start time.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> listAllEvents(
        com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListAllEventsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * List all events from the id.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse> listEventsFromId(
        com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getListEventsFromIdMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_SEND_EVENT = 0;
  private static final int METHODID_LIST_EVENTS = 1;
  private static final int METHODID_LIST_ALL_EVENTS = 2;
  private static final int METHODID_LIST_EVENTS_FROM_ID = 3;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final NotificationServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(NotificationServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_SEND_EVENT:
          serviceImpl.sendEvent((com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse>) responseObserver);
          break;
        case METHODID_LIST_EVENTS:
          serviceImpl.listEvents((com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>) responseObserver);
          break;
        case METHODID_LIST_ALL_EVENTS:
          serviceImpl.listAllEvents((com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>) responseObserver);
          break;
        case METHODID_LIST_EVENTS_FROM_ID:
          serviceImpl.listEventsFromId((com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsFromIdRequest) request,
              (io.grpc.stub.StreamObserver<com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse>) responseObserver);
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

  private static abstract class NotificationServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    NotificationServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.aiflow.notification.proto.NotificationServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("NotificationService");
    }
  }

  private static final class NotificationServiceFileDescriptorSupplier
      extends NotificationServiceBaseDescriptorSupplier {
    NotificationServiceFileDescriptorSupplier() {}
  }

  private static final class NotificationServiceMethodDescriptorSupplier
      extends NotificationServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    NotificationServiceMethodDescriptorSupplier(String methodName) {
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
      synchronized (NotificationServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new NotificationServiceFileDescriptorSupplier())
              .addMethod(getSendEventMethod())
              .addMethod(getListEventsMethod())
              .addMethod(getListAllEventsMethod())
              .addMethod(getListEventsFromIdMethod())
              .build();
        }
      }
    }
    return result;
  }
}
