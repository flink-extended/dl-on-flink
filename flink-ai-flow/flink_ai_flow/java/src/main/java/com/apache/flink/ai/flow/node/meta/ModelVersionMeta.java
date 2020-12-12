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
package com.apache.flink.ai.flow.node.meta;

import java.util.HashMap;
import java.util.Map;


/**
 * model version meta description
 */
public class ModelVersionMeta {
	private  String version;
	private  String versionUri;
	private  String metricUri;
	private  long createTime;
	private  String signature;
	private Map<String, String> properties = new HashMap<>();

	public String getVersion() {
		return version;
	}

	public void setVersion(String version) {
		this.version = version;
	}

	public String getVersionUri() {
		return versionUri;
	}

	public void setVersionUri(String versionUri) {
		this.versionUri = versionUri;
	}

	public String getMetricUri() {
		return metricUri;
	}

	public void setMetricUri(String metricUri) {
		this.metricUri = metricUri;
	}

	public long getCreateTime() {
		return createTime;
	}

	public void setCreateTime(long createTime) {
		this.createTime = createTime;
	}

	public String getSignature() {
		return signature;
	}

	public void setSignature(String signature) {
		this.signature = signature;
	}

	public Map<String, String> getProperties() {
		return properties;
	}

	public void setProperties(Map<String, String> properties) {
		this.properties = properties;
	}
}
