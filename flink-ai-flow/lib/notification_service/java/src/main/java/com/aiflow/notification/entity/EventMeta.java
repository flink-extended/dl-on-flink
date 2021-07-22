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
package com.aiflow.notification.entity;

import com.aiflow.notification.proto.NotificationServiceOuterClass.EventProto;

public class EventMeta {

    private String key;
    private String value;
    private String eventType;
    private long version;
    private long createTime;
    private String context;
    private String namespace;
    private String sender;

    public EventMeta(
            String key,
            String value,
            String eventType,
            long version,
            long createTime,
            String context,
            String namespace,
            String sender) {
        this.key = key;
        this.value = value;
        this.eventType = eventType;
        this.version = version;
        this.createTime = createTime;
        this.context = context;
        this.namespace = namespace;
        this.sender = sender;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getEventType() {
        return eventType;
    }

    public void setEventType(String eventType) {
        this.eventType = eventType;
    }

    public long getVersion() {
        return version;
    }

    public void setVersion(long version) {
        this.version = version;
    }

    public long getCreateTime() {
        return createTime;
    }

    public void setCreateTime(long createTime) {
        this.createTime = createTime;
    }

    public String getContext() {
        return context;
    }

    public void setContext(String context) {
        this.context = context;
    }

    public String getNamespace() {
        return namespace;
    }

    public void setNamespace(String namespace) {
        this.namespace = namespace;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }

    @Override
    public String toString() {
        return "EventMeta{"
                + "key='"
                + key
                + '\''
                + ", value='"
                + value
                + '\''
                + ", eventType='"
                + eventType
                + '\''
                + ", version="
                + version
                + ", createTime="
                + createTime
                + ", context='"
                + context
                + '\''
                + ", namespace='"
                + namespace
                + '\''
                + ", sender='"
                + sender
                + '\''
                + '}';
    }

    public static EventMeta buildEventMeta(EventProto eventProto) {
        return new EventMeta(
                eventProto.getKey(),
                eventProto.getValue(),
                eventProto.getEventType(),
                eventProto.getVersion(),
                eventProto.getCreateTime(),
                eventProto.getContext(),
                eventProto.getNamespace(),
                eventProto.getSender());
    }
}
