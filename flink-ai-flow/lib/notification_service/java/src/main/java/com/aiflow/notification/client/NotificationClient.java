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
import com.aiflow.notification.proto.NotificationServiceGrpc.NotificationServiceBlockingStub;
import com.aiflow.notification.proto.NotificationServiceOuterClass.EventProto;
import com.aiflow.notification.proto.NotificationServiceOuterClass.GetLatestVersionByKeyRequest;
import com.aiflow.notification.proto.NotificationServiceOuterClass.GetLatestVersionResponse;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ListAllEventsRequest;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsRequest;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ListEventsResponse;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ReturnStatus;
import com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventRequest;
import com.aiflow.notification.proto.NotificationServiceOuterClass.SendEventsResponse;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ListMembersRequest;
import com.aiflow.notification.proto.NotificationServiceOuterClass.ListMembersResponse;
import com.aiflow.notification.proto.NotificationServiceOuterClass.MemberProto;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.grpc.ManagedChannelBuilder;
import org.apache.commons.lang3.StringUtils;

import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static com.aiflow.notification.entity.EventMeta.buildEventMeta;
import static com.aiflow.notification.proto.NotificationServiceGrpc.newBlockingStub;

public class NotificationClient {

	public static final String SERVER_URI = "localhost:50051";

	private NotificationServiceBlockingStub notificationServiceStub;
	private Set<MemberProto> livingMembers;
	private Boolean enableHa;
	private String currentUri;
	private final String defaultNamespace;
	private final Integer listMemberIntervalMs;
	private final Integer retryIntervalMs;
	private final Integer retryTimeoutMs;
	private final Map<Map<String, String>, EventListener> threads;
	private final ExecutorService listMembersService;

	protected void initNotificationServiceStub() {
		this.notificationServiceStub =
				newBlockingStub(
						ManagedChannelBuilder.forTarget(
								StringUtils.isEmpty(this.currentUri) ? SERVER_URI : this.currentUri)
								.usePlaintext()
								.build());
		this.notificationServiceStub =
				wrapBlockingStub(
						this.notificationServiceStub,
						StringUtils.isEmpty(this.currentUri) ? SERVER_URI : this.currentUri,
						livingMembers,
						this.enableHa,
						this.retryIntervalMs,
						this.retryTimeoutMs);
	}

	public NotificationClient(
			String target,
			String defaultNamespace,
			Boolean enableHa,
			Integer listMemberIntervalMs,
			Integer retryIntervalMs,
			Integer retryTimeoutMs) throws Exception {
		this.defaultNamespace = defaultNamespace;
		this.enableHa = enableHa;
		this.listMemberIntervalMs = listMemberIntervalMs;
		this.retryIntervalMs = retryIntervalMs;
		this.retryTimeoutMs = retryTimeoutMs;
		if (this.enableHa) {
			String[] serverUris = StringUtils.split(target, ",");
			boolean lastError = false;
			for (String serverUri: serverUris) {
				this.currentUri = serverUri;
				this.initNotificationServiceStub();
				ListMembersRequest request = ListMembersRequest.newBuilder().setTimeoutSeconds(this.listMemberIntervalMs / 1000).build();
				ListMembersResponse response = this.notificationServiceStub.listMembers(request);
				if (response.getReturnCode() == ReturnStatus.SUCCESS) {
					this.livingMembers = new HashSet<>(response.getMembersList());
					lastError = false;
					break;
				} else {
					lastError = true;
				}
			}
			if (lastError) {
				throw new Exception("No available server uri!");
			}
		} else {
			this.currentUri = target;
			this.initNotificationServiceStub();
		}
		this.threads = new HashMap<>();
		this.livingMembers = new HashSet<>();
		this.listMembersService = Executors.newSingleThreadExecutor(
				new ThreadFactoryBuilder()
						.setDaemon(true)
						.setNameFormat("listen-notification-%d")
						.build());
		this.listMembersService.submit(this.listMembers());
	}

	/**
	 * List living members under high available mode
	 */
	protected Runnable listMembers() {
		return () -> {
			while (this.enableHa) {
				try {
					if (Thread.currentThread().isInterrupted()) {
						break;
					}
					ListMembersRequest request = ListMembersRequest.newBuilder().setTimeoutSeconds(this.listMemberIntervalMs / 1000).build();
					ListMembersResponse response = this.notificationServiceStub.listMembers(request);
					if (response.getReturnCode() == ReturnStatus.SUCCESS) {
						this.livingMembers = new HashSet<>(response.getMembersList());
					} else {
						throw new Exception(response.getReturnMsg());
					}
				} catch (Exception e) {
					e.printStackTrace();
					throw new RuntimeException("Error while listening notification", e);
				}
			}
		};
	}

	/**
	 * Disable high availability mode
	 */
	public void disableHighAvailability() {
		this.enableHa = false;
		this.listMembersService.shutdown();
	}

	/**
	 * Send the event to Notification Service.
	 *
	 * @param key Key of event updated in Notification Service.
	 * @param value Value of event updated in Notification Service.
	 * @param eventType Type of event updated in Notification Service.
	 * @param context Context of event updated in Notification Service.
	 * @return Object of Event created in Notification Service.
	 */
	public EventMeta sendEvent(String key, String value, String eventType, String context)
			throws Exception {
		SendEventRequest request =
				SendEventRequest.newBuilder()
						.setEvent(
								EventProto.newBuilder()
										.setKey(key)
										.setValue(value)
										.setEventType(eventType)
										.setContext(context)
										.setNamespace(defaultNamespace)
										.build())
						.setUuid(UUID.randomUUID().toString())
						.build();
		SendEventsResponse response = this.notificationServiceStub.sendEvent(request);
		if (response.getReturnCode() == ReturnStatus.SUCCESS) {
			return buildEventMeta(response.getEvent());
		} else {
			throw new Exception(response.getReturnMsg());
		}
	}

	/**
	 * List specific `key` or `version` notifications in Notification Service.
	 *
	 * @param keys Keys of notification for listening.
	 * @param version (Optional) Version of notification for listening.
	 * @param eventType (Optional) Type of event for listening.
	 * @param startTime (Optional) Type of event for listening.
	 * @return List of Notification updated in Notification Service.
	 */
	public List<EventMeta> listEvents(
			List<String> keys, long version, String eventType, long startTime) throws Exception {
		return listEvents(
				this.notificationServiceStub,
				keys,
				version,
				eventType,
				startTime,
				defaultNamespace,
				0);
	}

	/**
	 * List specific registered listener events in Notification Service.
	 *
	 * @param serviceStub Notification service GRPC stub.
	 * @param keys Keys of event for listening.
	 * @param version (Optional) Version of event for listening.
	 * @param timeoutSeconds List events request timeout seconds.
	 * @return List of event updated in Notification Service.
	 */
	protected static List<EventMeta> listEvents(
			NotificationServiceBlockingStub serviceStub,
			List<String> keys,
			long version,
			String eventType,
			long startTime,
			String namespace,
			Integer timeoutSeconds)
			throws Exception {
		ListEventsRequest request =
				ListEventsRequest.newBuilder()
						.addAllKeys(keys)
						.setStartVersion(version)
						.setEventType(eventType)
						.setStartTime(startTime)
						.setNamespace(namespace)
						.setTimeoutSeconds(timeoutSeconds)
						.build();
		return parseEventsFromResponse(serviceStub.listEvents(request));
	}

	/**
	 * List all registered listener events in Notification Service.
	 *
	 * @param startTime (Optional) The event create time after the given startTime.
	 * @param startVersion (Optional) Start version of event for listening.
	 * @param endVersion (Optional) End version of event for listening.
	 * @return List of event updated in Notification Service.
	 */
	public List<EventMeta> listAllEvents(long startTime, long startVersion, long endVersion)
			throws Exception {
		ListAllEventsRequest request =
				ListAllEventsRequest.newBuilder()
						.setStartTime(startTime)
						.setStartVersion(startVersion)
						.setEndVersion(endVersion)
						.build();
		ListEventsResponse response = this.notificationServiceStub.listAllEvents(request);
		return parseEventsFromResponse(response);
	}

	private static List<EventMeta> parseEventsFromResponse(ListEventsResponse response)
			throws Exception {
		if (response.getReturnCode() == ReturnStatus.SUCCESS) {
			List<EventMeta> eventMetas = new ArrayList<>();
			for (EventProto eventProto : response.getEventsList()) {
				eventMetas.add(buildEventMeta(eventProto));
			}
			return eventMetas;
		} else {
			throw new Exception(response.getReturnMsg());
		}
	}

	/**
	 * Start listen specific `key` or `version` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 * @param watcher Watcher instance for listening notification.
	 * @param version (Optional) Version of notification for listening.
	 * @param eventType (Optional) Type of event for listening.
	 * @param startTime (Optional) Type of event for listening.
	 */
	public void startListenEvent(String key, EventWatcher watcher, long version, String eventType, long startTime) {
		String namespace = this.defaultNamespace;
		Map<String, String> listenKey = new HashMap<String, String>() {{
			put(key, namespace);
		}};
		if (!this.threads.containsKey(listenKey)) {
			ArrayList<String> curListenerKeys = new ArrayList<String>(){{add(key);}};
			EventListener listener = new EventListener(this.notificationServiceStub,
					curListenerKeys, version, eventType, startTime, namespace, watcher, 5);
			listener.start();
			this.threads.put(listenKey, listener);
		}
	}

	/**
	 * Stop listen specific `key` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 */
	public void stopListenEvent(String key) {
		String namespace = this.defaultNamespace;
		Map<String, String> listenKey = new HashMap<String, String>(){{put(key, namespace);}};
		if (StringUtils.isEmpty(key)) {
			for (Map.Entry<Map<String, String>, EventListener> entry : threads.entrySet()) {
				entry.getValue().shutdown();
			}
		} else {
			if(this.threads.containsKey(listenKey)) {
				this.threads.get(listenKey).shutdown();
			}
		}
	}

	/**
	 * Get latest version of specific `key` notifications in Notification Service.
	 *
	 * @param key Key of notification for listening.
	 */
	public long getLatestVersion(String key) throws Exception {
		if (StringUtils.isEmpty(key)) {
			throw new Exception("Empty key, please provide valid key");
		} else {
			GetLatestVersionByKeyRequest request =
					GetLatestVersionByKeyRequest.newBuilder().setKey(key).build();
			GetLatestVersionResponse response =
					this.notificationServiceStub.getLatestVersionByKey(request);
			return parseLatestVersionFromResponse(response);
		}
	}

	protected static NotificationServiceBlockingStub wrapBlockingStub(
			NotificationServiceBlockingStub stub,
			String target,
			Set<MemberProto> livingMembers,
			Boolean haRunning,
			Integer retryIntervalMs,
			Integer retryTimeoutMs) {
		return newBlockingStub(ManagedChannelBuilder.forTarget(target).usePlaintext().build())
				.withInterceptors(
						new NotificationInterceptor(
								stub,
								target,
								livingMembers,
								haRunning,
								retryIntervalMs,
								retryTimeoutMs));
	}

	public long parseLatestVersionFromResponse(GetLatestVersionResponse response)
			throws Exception {
		if (response.getReturnCode().equals(ReturnStatus.ERROR.toString())) {
			throw new Exception(response.getReturnMsg());
		} else {
			return response.getVersion();
		}
	}

}
