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

import com.aiflow.notification.proto.NotificationServiceGrpc;
import com.aiflow.notification.proto.NotificationServiceOuterClass.*;
import io.grpc.ManagedChannelBuilder;
import com.google.protobuf.util.JsonFormat.Parser;
import io.grpc.Channel;
import org.apache.commons.lang3.StringUtils;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.google.protobuf.util.JsonFormat.parser;


public class NotificationClient {
	public static final String SERVER_URI = "localhost:50051";

	private final NotificationServiceGrpc.NotificationServiceBlockingStub notificationServiceStub;
	private final Map<String, EventListener> threads;

	private final Parser parser = parser().ignoringUnknownFields();

	public NotificationClient() {
		this(SERVER_URI);
	}

	public NotificationClient(String target) {
		this(ManagedChannelBuilder.forTarget(target).usePlaintext().build());
	}

	public NotificationClient(Channel channel) {
		this.notificationServiceStub = NotificationServiceGrpc.newBlockingStub(channel);
		this.threads = new HashMap<>();
	}

	public static Event eventProtoToEvent(EventProto eventProto) {
		return new Event(eventProto.getKey(), eventProto.getValue(), eventProto.getEventType(),
			eventProto.getVersion(), eventProto.getCreateTime(), eventProto.getId());
	}

	/**
	 * Send the event to Notification Service.
	 *
	 * @param key Key of event updated in Notification Service.
	 * @param value Value of event updated in Notification Service.
	 * @return Object of Event created in Notification Service.
	 */
	public Event sendEvent(String key, String value, String eventType) throws Exception {
		SendEventRequest request = SendEventRequest.newBuilder()
			.setEvent(EventProto.newBuilder().setKey(key).setValue(value).setEventType(eventType).build()).build();
		SendEventsResponse response = this.notificationServiceStub.sendEvent(request);
		if (response.getReturnCode().equals(ReturnStatus.ERROR.toString())) {
			throw new Exception(response.getReturnMsg());
		} else {
			EventProto eventProto = response.getEvent();
			return eventProtoToEvent(eventProto);
		}
	}

	/**
	 * List specific `key` or `version` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 * @param version (Optional) Version of notification for listening.
	 * @return List of Notification updated in Notification Service.
	 */
	public List<Event> listEvents(String key, int version) throws Exception {
		return listEvents(this.notificationServiceStub, key, version, 0);
	}

	/**
	 * List specific registered listener events in Notification Service.
	 *
	 * @param serviceStub Notification service GRPC stub.
	 * @param key Key of event for listening.
	 * @param version (Optional) Version of event for listening.
	 * @param timeoutSeconds List events request timeout seconds.
	 * @return List of event updated in Notification Service.
	 */
	public static List<Event> listEvents(
		NotificationServiceGrpc.NotificationServiceBlockingStub serviceStub, String key, int version,
		Integer timeoutSeconds) throws Exception {
		ListEventsRequest request = ListEventsRequest.newBuilder()
			.setEvent(EventProto.newBuilder().setKey(key)
				.setVersion(version).build()).setTimeoutSeconds(timeoutSeconds).build();
		ListEventsResponse response = serviceStub.listEvents(request);
		return parseEventsFromResponse(response);
	}

	/**
	 *
	 * @param startTime The event create time after the given startTime.
	 * @return List of event updated in Notification Service.
	 * @throws Exception
	 */
	public List<Event> listAllEvents(long startTime) throws Exception {
		ListAllEventsRequest request = ListAllEventsRequest.newBuilder().setStartTime(startTime).build();
		ListEventsResponse response = this.notificationServiceStub.listAllEvents(request);
		return parseEventsFromResponse(response);
	}

	private static List<Event> parseEventsFromResponse(ListEventsResponse response)
		throws Exception {
		if (response.getReturnCode().equals(ReturnStatus.ERROR.toString())) {
			throw new Exception(response.getReturnMsg());
		} else {
			List<Event> result = new ArrayList<>();
			for (EventProto eventProto : response.getEventsList()) {
				result.add(eventProtoToEvent(eventProto));
			}
			return result;
		}
	}

	/**
	 *
	 * @param id The event id after the given id.
	 * @return List of event updated in Notification Service.
	 * @throws Exception
	 */
	public List<Event> listEventsFromId(long id) throws Exception {
		ListEventsFromIdRequest request = ListEventsFromIdRequest.newBuilder().setId(id).build();
		ListEventsResponse response = this.notificationServiceStub.listEventsFromId(request);
		return parseEventsFromResponse(response);
	}

	/**
	 * Start listen specific `key` or `version` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 * @param watcher Watcher instance for listening notification.
	 * @param version (Optional) Version of notification for listening.
	 */
	public void startListenEvent(String key, EventWatcher watcher, Integer version) {
		if (!this.threads.containsKey(key)) {
			EventListener listener = new EventListener(this.notificationServiceStub,
				key, version, watcher, 5);
			listener.start();
			this.threads.put(key, listener);
		}
	}

	/**
	 * Stop listen specific `key` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 */
	public void stopListenEvent(String key) {
		if (StringUtils.isEmpty(key)) {
			for (Map.Entry<String, EventListener> entry : threads.entrySet()) {
				entry.getValue().shutdown();
			}
		} else {
			if(this.threads.containsKey(key)) {
				this.threads.get(key).shutdown();
			}
		}
	}

}
