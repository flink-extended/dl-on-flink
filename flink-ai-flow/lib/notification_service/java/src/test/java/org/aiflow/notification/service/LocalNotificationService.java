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
package org.aiflow.notification.service;

import io.grpc.stub.StreamObserver;
import org.aiflow.notification.proto.NotificationServiceGrpc;
import org.aiflow.notification.proto.NotificationServiceOuterClass;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LocalNotificationService extends NotificationServiceGrpc.NotificationServiceImplBase {
    private List<NotificationServiceOuterClass.EventProto> store = new ArrayList<>();
    private Map<String, Long> versionMap = new HashMap<>();
    private Long id = 0l;

    @Override
    public void sendEvent(
            NotificationServiceOuterClass.SendEventRequest request,
            StreamObserver<NotificationServiceOuterClass.SendEventsResponse> responseObserver) {
        id++;
        if (!versionMap.containsKey(request.getEvent().getKey())) {
            versionMap.put(request.getEvent().getKey(), 0L);
        }
        Long version = versionMap.get(request.getEvent().getKey());
        version++;
        versionMap.put(request.getEvent().getKey(), version);

        NotificationServiceOuterClass.EventProto eventProto =
                NotificationServiceOuterClass.EventProto.newBuilder()
                        .setKey(request.getEvent().getKey())
                        .setValue(request.getEvent().getValue())
                        .setEventType(request.getEvent().getEventType())
                        .setCreateTime(System.nanoTime())
                        .setVersion(version.intValue())
                        .build();

        store.add(eventProto);
        NotificationServiceOuterClass.SendEventsResponse response =
                NotificationServiceOuterClass.SendEventsResponse.newBuilder()
                        .setEvent(eventProto)
                        .setReturnCode(NotificationServiceOuterClass.ReturnStatus.SUCCESS)
                        .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void listEvents(
            NotificationServiceOuterClass.ListEventsRequest request,
            StreamObserver<NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
        String key = request.getKeys(0);
        long version = request.getStartVersion();
        List<NotificationServiceOuterClass.EventProto> eventProtos = new ArrayList<>();
        for (NotificationServiceOuterClass.EventProto eventProto : store) {
            if (key.equals(eventProto.getKey()) && eventProto.getVersion() > version) {
                eventProtos.add(eventProto);
            }
        }
        if (request.getTimeoutSeconds() > 0 && eventProtos.size() == 0) {
            try {
                Thread.sleep(request.getTimeoutSeconds() * 1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        NotificationServiceOuterClass.ListEventsResponse response =
                NotificationServiceOuterClass.ListEventsResponse.newBuilder()
                        .addAllEvents(eventProtos)
                        .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void listAllEvents(
            NotificationServiceOuterClass.ListAllEventsRequest request,
            StreamObserver<NotificationServiceOuterClass.ListEventsResponse> responseObserver) {
        List<NotificationServiceOuterClass.EventProto> eventProtos = new ArrayList<>();
        for (NotificationServiceOuterClass.EventProto eventProto : store) {
            if (eventProto.getCreateTime() >= request.getStartTime()) {
                eventProtos.add(eventProto);
            }
        }
        NotificationServiceOuterClass.ListEventsResponse response =
                NotificationServiceOuterClass.ListEventsResponse.newBuilder()
                        .addAllEvents(eventProtos)
                        .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void getLatestVersionByKey(
            NotificationServiceOuterClass.GetLatestVersionByKeyRequest request,
            StreamObserver<NotificationServiceOuterClass.GetLatestVersionResponse>
                    responseObserver) {
        long latestVersion = this.id;
        NotificationServiceOuterClass.GetLatestVersionResponse response =
                NotificationServiceOuterClass.GetLatestVersionResponse.newBuilder()
                        .setVersion(latestVersion)
                        .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}
