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

import org.aiflow.notification.entity.EventMeta;
import org.aiflow.notification.service.PythonServer;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.Collections;
import java.util.List;
import java.util.Properties;

import static org.aiflow.notification.conf.Configuration.CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY;
import static org.aiflow.notification.conf.Configuration.CLIENT_ID_CONFIG_KEY;
import static org.aiflow.notification.conf.Configuration.CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_KEY;
import static org.junit.Assert.assertEquals;

public class NotificationClientTest {

    private static NotificationClient client;
    private static PythonServer server;

    @BeforeClass
    public static void setUp() throws Exception {
        server = new PythonServer();
        server.start();
        // waiting for notification server
        Thread.sleep(1000);
        // Create a NotificationClient using the in-process channel
        try {
            Properties properties = new Properties();
            properties.put(CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY, "true");
            client =
                    new NotificationClient(
                            "localhost:50051", "default", "test", false, 5, 10, 2000, properties);
        } catch (Exception e) {
            throw new Exception("Failed to init notification client", e);
        }
    }

    @AfterClass
    public static void tearDown() throws InterruptedException {
        server.stop();
    }

    @Test
    public void sendEvent() throws Exception {
        long latestVersion = this.client.getLatestVersion("default", "key");
        for (int i = 0; i < 3; i++) {
            this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        List<String> listenerKeys = Collections.singletonList("key");
        List<EventMeta> eventList =
                this.client.listEvents("default", listenerKeys, latestVersion, "type", 0, "");
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
        long latestVersion = this.client.getLatestVersion("default", "key");
        for (int i = 0; i < 3; i++) {
            this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        final Integer[] ii = {0};
        String listenerKey = "key";
        this.client.startListenEvent(
                "default",
                listenerKey,
                events -> ii[0] += events.size(),
                latestVersion,
                "type",
                0,
                "*");

        Thread.sleep(10000);
        assertEquals(3, ii[0].intValue());
        this.client.stopListenEvent("default", listenerKey, "type", "*");
    }

    @Test
    public void startListenEventFilterByKey() throws Exception {
        long latestVersion = sendTestEvents();
        final Integer[] ii = {0};
        String listenerKey = "key_0";
        this.client.startListenEvent(
                "default",
                listenerKey,
                events -> ii[0] += events.size(),
                latestVersion,
                "*",
                0,
                "*");
        Thread.sleep(10000);
        assertEquals(1, ii[0].intValue());
        this.client.stopListenEvent("default", listenerKey, "*", "*");
    }

    @Test
    public void startListenEventSetSender() throws Exception {
        long latestVersion = sendTestEvents();
        final Integer[] ii = {0};
        String listenerKey = "*";
        this.client.startListenEvent(
                "default",
                listenerKey,
                events -> ii[0] += events.size(),
                latestVersion,
                "*",
                0,
                "test");
        Thread.sleep(10000);
        assertEquals(3, ii[0].intValue());
        this.client.stopListenEvent("default", listenerKey, "*", "test");
    }

    @Test
    public void startListenEventFilterBySender() throws Exception {
        long latestVersion = sendTestEvents();
        final Integer[] ii = {0};
        String listenerKey = "*";
        this.client.startListenEvent(
                "default",
                listenerKey,
                events -> ii[0] += events.size(),
                latestVersion,
                "*",
                0,
                "test_1");
        Thread.sleep(10000);
        assertEquals(0, ii[0].intValue());
        this.client.stopListenEvent("default", listenerKey, "*", "test_1");
    }

    @Test
    public void startListenEventFilterByEventType() throws Exception {
        long latestVersion = sendTestEvents();
        final Integer[] ii = {0};
        String listenerKey = "*";
        this.client.startListenEvent(
                "default",
                listenerKey,
                events -> ii[0] += events.size(),
                latestVersion,
                "type_1",
                0,
                "test");
        Thread.sleep(10000);
        assertEquals(1, ii[0].intValue());
        this.client.stopListenEvent("default", listenerKey, "type_1", "test");
    }

    private long sendTestEvents() throws Exception {
        long latestVersion = this.client.getLatestVersion("default", "key");
        for (int i = 0; i < 3; i++) {
            this.client.sendEvent(
                    String.format("key_%d", i), String.valueOf(i), String.format("type_%d", i), "");
        }
        return latestVersion;
    }

    @Test
    public void getLatestVersion() throws Exception {
        long latestVersion = this.client.getLatestVersion("default", "key");
        for (int i = 0; i < 3; i++) {
            this.client.sendEvent("key", String.valueOf(i), "type", "");
        }
        long newLatestVersion = this.client.getLatestVersion("default", "key");
        assertEquals(latestVersion + 3, newLatestVersion);
    }

    @Test
    public void testSendEventIdempotence() throws Exception {
        Properties properties = new Properties();
        String key = "test_idempotence_key";
        properties.put(CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY, "true");
        NotificationClient idempotent_client =
                new NotificationClient(
                        "localhost:50051", "default", "test", false, 5, 10, 2000, properties);
        assertEquals(0, idempotent_client.getSequenceNum().get());
        idempotent_client.sendEvent(key, "value1", "type", "");

        List<String> keyList = Collections.singletonList(key);
        assertEquals(
                1, idempotent_client.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(1, idempotent_client.getSequenceNum().get());

        idempotent_client.sendEvent(key, "value2", "type", "");
        assertEquals(
                2, idempotent_client.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(2, idempotent_client.getSequenceNum().getAndDecrement());

        idempotent_client.sendEvent(key, "value3", "type", "");
        assertEquals(
                2, idempotent_client.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(2, idempotent_client.getSequenceNum().getAndDecrement());
    }

    @Test
    public void testClientRecovery() throws Exception {
        Properties properties = new Properties();
        String key = "test_client_recovery_key";
        properties.put(CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY, "true");
        NotificationClient client1 =
                new NotificationClient(
                        "localhost:50051", "default", "test", false, 5, 10, 2000, properties);
        assertEquals(0, client1.getSequenceNum().get());
        client1.sendEvent(key, "value1", "type", "");
        client1.sendEvent(key, "value2", "type", "");
        client1.sendEvent(key, "value3", "type", "");

        List<String> keyList = Collections.singletonList(key);
        assertEquals(3, client1.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(3, client1.getSequenceNum().get());

        properties.put(CLIENT_ID_CONFIG_KEY, client1.getClientId().toString());
        properties.put(CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_KEY, "2");
        NotificationClient client2 =
                new NotificationClient(
                        "localhost:50051", "default", "test", false, 5, 10, 2000, properties);
        client2.sendEvent(key, "value4", "type", "");
        assertEquals(3, client2.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(3, client2.getSequenceNum().get());

        client2.sendEvent(key, "value5", "type", "");
        assertEquals(4, client2.listEvents("default", keyList, 0, "type", 0, "test").size());
        assertEquals(4, client2.getSequenceNum().get());
    }
}
