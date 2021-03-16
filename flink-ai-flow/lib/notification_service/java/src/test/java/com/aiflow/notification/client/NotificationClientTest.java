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
package com.aiflow.notification.client;

import com.aiflow.notification.entity.EventMeta;
import com.aiflow.notification.service.LocalNotificationService;
import io.grpc.ManagedChannel;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.testing.GrpcCleanupRule;
import io.grpc.util.MutableHandlerRegistry;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertEquals;

public class NotificationClientTest {
    @Rule public final GrpcCleanupRule grpcCleanup = new GrpcCleanupRule();
    private final MutableHandlerRegistry serviceRegistry = new MutableHandlerRegistry();
    private NotificationClient client;
    private LocalNotificationService mockNotificationService = new LocalNotificationService();

    @Before
    public void setUp() throws Exception {
        // Generate a unique in-process server name.
        String serverName = InProcessServerBuilder.generateName();

        // Create a server, add service, start, and register for automatic graceful shutdown.
        this.grpcCleanup.register(
                InProcessServerBuilder.forName(serverName)
                        .directExecutor()
                        .fallbackHandlerRegistry(this.serviceRegistry)
                        .addService(mockNotificationService)
                        .build()
                        .start());

        // Create a client channel and register for automatic graceful shutdown.
        ManagedChannel channel =
                this.grpcCleanup.register(
                        InProcessChannelBuilder.forName(serverName).directExecutor().build());

        // Create a NotificationClient using the in-process channel
        try {
            this.client =
                    new NotificationClient(
                            "localhost:50051,localhost:50052", "default", true, 5, 10, 2000);
        } catch (Exception e) {
            throw new Exception("Failed to init notification client", e);
        }
    }

    @Test
    public void sendEvent() throws Exception {
        long latestVersion = this.client.getLatestVersion("key");
        for (int i = 0; i < 3; i++) {
            EventMeta event = this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        ArrayList<String> listenerKeys =
                new ArrayList<String>() {
                    {
                        add("key");
                    }
                };
        long startTime = System.currentTimeMillis();
        List<EventMeta> eventList = this.client.listEvents(listenerKeys, latestVersion, "type", 0);
        assertEquals(3, eventList.size());
    }

    @Test
    public void listAllEvents() throws Exception {
        long startTime = 0;
        for (int i = 0; i < 3; i++) {
            EventMeta event = this.client.sendEvent("key", String.valueOf(i), "type", "");
            if (i == 1) {
                startTime = event.getCreateTime();
            }
        }
        List<EventMeta> eventList = this.client.listAllEvents(startTime, 0, 0);
        assertEquals(2, eventList.size());
    }

    @Test
    public void startListenEvent() throws Exception {
        long latestVersion = this.client.getLatestVersion("key");
        for (int i = 0; i < 3; i++) {
            EventMeta event = this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        final Integer[] ii = {0};
        String listenerKey = "key";
        this.client.startListenEvent(
                listenerKey,
                new EventWatcher() {
                    @Override
                    public void process(List<EventMeta> events) {
                        ii[0] += events.size();
                    }
                },
                latestVersion,
                "type",
                0);

        Thread.sleep(10000);
        assertEquals(3, ii[0].intValue());
    }

    @Test
    public void getLatestVersion() throws Exception {
        long latestVersion = this.client.getLatestVersion("key");
        for (int i = 0; i < 3; i++) {
            EventMeta event = this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        long newLatestVersion = this.client.getLatestVersion("key");
        assertEquals(latestVersion + 3, newLatestVersion);
    }
}
