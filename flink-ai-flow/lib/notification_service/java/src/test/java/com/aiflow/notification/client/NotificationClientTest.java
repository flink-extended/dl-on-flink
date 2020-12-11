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

import com.aiflow.notification.service.LocalNotificationService;
import io.grpc.ManagedChannel;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.testing.GrpcCleanupRule;
import io.grpc.util.MutableHandlerRegistry;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import java.io.IOException;
import java.util.List;

import static org.junit.Assert.*;

public class NotificationClientTest {
	private NotificationClient client;

	@Rule
	public final GrpcCleanupRule grpcCleanup = new GrpcCleanupRule();
	private final MutableHandlerRegistry serviceRegistry = new MutableHandlerRegistry();
	private LocalNotificationService mockNotificationService = new LocalNotificationService();

	@Before
	public void setUp() throws IOException {
		// Generate a unique in-process server name.
		String serverName = InProcessServerBuilder.generateName();

		// Create a server, add service, start, and register for automatic graceful shutdown.
		this.grpcCleanup.register(InProcessServerBuilder
			.forName(serverName).directExecutor().fallbackHandlerRegistry(this.serviceRegistry)
			.addService(mockNotificationService).build().start());

		// Create a client channel and register for automatic graceful shutdown.
		ManagedChannel channel = this.grpcCleanup.register(
			InProcessChannelBuilder.forName(serverName).directExecutor().build());

		// Create a NotificationClient using the in-process channel
		this.client = new NotificationClient(channel);
	}

	@Test
	public void sendEvent() throws Exception {
		for(int i = 0; i <3; i++) {
			Event event =this.client.sendEvent("key", String.valueOf(i), "type");
		}
		List<Event> eventList = this.client.listEvents("key", 0);
		assertEquals(3, eventList.size());
	}

	@Test
	public void listAllEvents() throws Exception{
		long startTime=0;
		for(int i = 0; i <3; i++) {
			Event event =this.client.sendEvent("key", String.valueOf(i), "type");
			if(i == 1){
				startTime = event.getCreate_time();
			}
		}
		List<Event> eventList = this.client.listAllEvents(startTime);
		assertEquals(2, eventList.size());
	}

	@Test
	public void listEventsFromId() throws Exception {
		for(int i = 0; i <3; i++) {
			Event event =this.client.sendEvent("key", String.valueOf(i), "type");
		}
		List<Event> eventList = this.client.listEventsFromId(1l);
		assertEquals(2, eventList.size());
	}

	@Test
	public void startListenEvent() throws Exception{
		for(int i = 0; i <3; i++) {
			Event event =this.client.sendEvent("key", String.valueOf(i), "type");

		}
		final Integer[] ii = { 0 };
		this.client.startListenEvent("key", new EventWatcher() {
			@Override
			public void process(List<Event> events) {
				ii[0] += events.size();
			}
		}, 0);

		Thread.sleep(1000);
		this.client.stopListenEvent("key");
		assertEquals(3, ii[0].intValue());
	}

}