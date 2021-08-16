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

import io.grpc.*;
import org.aiflow.notification.proto.NotificationServiceGrpc;
import org.aiflow.notification.proto.NotificationServiceOuterClass.MemberProto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashSet;
import java.util.Set;

import static org.aiflow.notification.client.NotificationClient.wrapBlockingStub;

public class NotificationInterceptor implements ClientInterceptor {

    private static final Logger logger = LoggerFactory.getLogger(NotificationInterceptor.class);
    private NotificationServiceGrpc.NotificationServiceBlockingStub stub;
    private String target;
    private Set<MemberProto> livingMembers;
    private Boolean haRunning;
    private Integer retryIntervalMs;
    private Integer retryTimeoutMs;

    public NotificationInterceptor(
            NotificationServiceGrpc.NotificationServiceBlockingStub stub,
            String target,
            Set<MemberProto> livingMembers,
            Boolean haRunning,
            Integer retryIntervalMs,
            Integer retryTimeoutMs) {
        this.stub = stub;
        this.target = target;
        this.livingMembers = livingMembers;
        this.haRunning = haRunning;
        this.retryIntervalMs = retryIntervalMs;
        this.retryTimeoutMs = retryTimeoutMs;
    }

    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> methodDescriptor,
            CallOptions callOptions,
            Channel channel) {
        final Long startTime = System.currentTimeMillis();
        final Set<String> failedMembers = new HashSet<>();
        while (true) {
            try {
                return channel.newCall(methodDescriptor, callOptions);
            } catch (Exception e) {
                failedMembers.add(target);
                boolean foundNewMember = false;
                for (MemberProto livingMember : livingMembers) {
                    if (foundNewMember) break;
                    if (failedMembers.contains(livingMember.getServerUri())) continue;
                    stub =
                            wrapBlockingStub(
                                    stub,
                                    livingMember.getServerUri(),
                                    livingMembers,
                                    haRunning,
                                    retryIntervalMs,
                                    retryTimeoutMs);
                    target = livingMember.getServerUri();
                    foundNewMember = true;
                }
                if (!foundNewMember) {
                    failedMembers.clear();
                }
            }
            if (!haRunning || System.currentTimeMillis() > startTime + retryTimeoutMs) {
                if (!haRunning) {
                    logger.warn("HA has been disabled.");
                } else {
                    logger.warn("Rpc retry timeout!");
                }
            }
        }
    }
}
