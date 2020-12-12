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
package com.apache.flink.ai.flow.node;

import com.alibaba.fastjson.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class BaseNode implements NodeParser{
	protected String id;
	protected String name;
	protected String type;
	protected Map<String, String> properties = new HashMap<String, String>();

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Map<String, String> getProperties() {
		return properties;
	}

	public void setProperties(Map<String, String> properties) {
		this.properties = properties;
	}

	public String getProperty(String key){
		return properties.get(key);
	}

	public void setProperty(String key, String value){
		properties.put(key, value);
	}

	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public BaseNode parseFromJSONObject(JSONObject jsonObject) throws Exception {
		this.setType(jsonObject.getString("__class__"));
		this.setId(jsonObject.getString("instance_id"));
		this.setName(jsonObject.getString("name"));
		JSONObject prop = jsonObject.getJSONObject("properties");
		for(Map.Entry<String, Object> entry: prop.entrySet()){
			this.setProperty(entry.getKey(), (String)entry.getValue());
		}
		return this;
	}
}
