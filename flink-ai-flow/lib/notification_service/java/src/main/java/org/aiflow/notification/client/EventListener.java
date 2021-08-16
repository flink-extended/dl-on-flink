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
package org.aiflow.notification.client;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import org.aiflow.notification.entity.EventMeta;
import org.aiflow.notification.proto.NotificationServiceGrpc;
import org.apache.commons.collections4.CollectionUtils;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.aiflow.notification.client.NotificationClient.listEvents;

public class EventListener {

    private final NotificationServiceGrpc.NotificationServiceBlockingStub serviceStub;
    private final List<String> keys;
    private final long version;
    private final String eventType;
    private final long startTime;
    private final String namespace;
    private final String sender;
    private final EventWatcher watcher;
    private final ExecutorService executorService;
    private final int timeoutSeconds;
    private volatile boolean isRunning = true;

    public EventListener(
            NotificationServiceGrpc.NotificationServiceBlockingStub serviceStub,
            List<String> keys,
            long version,
            String eventType,
            long startTime,
            String namespace,
            String sender,
            EventWatcher watcher,
            Integer timeoutSeconds) {
        this.serviceStub = serviceStub;
        this.keys = keys;
        this.version = version;
        this.eventType = eventType;
        this.startTime = startTime;
        this.namespace = namespace;
        this.sender = sender;
        this.watcher = watcher;
        this.timeoutSeconds = timeoutSeconds;
        this.executorService =
                Executors.newSingleThreadExecutor(
                        new ThreadFactoryBuilder()
                                .setDaemon(true)
                                .setNameFormat("listen-notification-%d")
                                .build());
    }

    public void start() {
        this.executorService.submit(listenEvents());
    }

    public void shutdown() {
        this.isRunning = false;
        this.executorService.shutdown();
    }

    public Runnable listenEvents() {
        return () -> {
            long listenVersion = this.version;
            while (this.isRunning) {
                try {
                    if (Thread.currentThread().isInterrupted()) {
                        break;
                    }
                    List<EventMeta> events =
                            listEvents(
                                    this.serviceStub,
                                    this.namespace,
                                    this.sender,
                                    this.keys,
                                    listenVersion,
                                    this.eventType,
                                    this.startTime,
                                    this.timeoutSeconds);
                    if (CollectionUtils.isNotEmpty(events)) {
                        this.watcher.process(events);
                        listenVersion = events.get(events.size() - 1).getVersion();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    throw new RuntimeException("Error while listening notification", e);
                }
            }
        };
    }
}
