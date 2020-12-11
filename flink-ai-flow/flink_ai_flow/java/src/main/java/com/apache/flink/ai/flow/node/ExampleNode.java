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

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class ExampleNode extends BaseNode{
	private String batchUri;
	private String streamUri;
	private String dataFormat;
	private String[] fieldNames;
	private String[] dataTypes;
	private Map<String, String> batchArgs = new HashMap<>();
	private Map<String, String> streamArgs = new HashMap<>();
	private boolean isSource = true;

//	flink catalog
	private String catalogName;
	private String catalogType;
	private String catalogDataBase;
	private String catalogConnectionUri;
	private String catalogVersion;
	private String catalogTable;
	private boolean isCatalog = false;

	public String getBatchUri() {
		return batchUri;
	}

	public void setBatchUri(String batchUri) {
		this.batchUri = batchUri;
	}

	public String getStreamUri() {
		return streamUri;
	}

	public void setStreamUri(String streamUri) {
		this.streamUri = streamUri;
	}

	public String getDataFormat() {
		return dataFormat;
	}

	public void setDataFormat(String dataFormat) {
		this.dataFormat = dataFormat;
	}

	public String[] getFieldNames() {
		return fieldNames;
	}

	public void setFieldNames(String[] fieldNames) {
		this.fieldNames = fieldNames;
	}

	public String[] getDataTypes() {
		return dataTypes;
	}

	public void setDataTypes(String[] dataTypes) {
		this.dataTypes = dataTypes;
	}

	public boolean isSource() {
		return isSource;
	}

	public void setSource(boolean source) {
		isSource = source;
	}

	public String getCatalogName() {
		return catalogName;
	}

	public void setCatalogName(String catalogName) {
		this.catalogName = catalogName;
	}

	public String getCatalogType() {
		return catalogType;
	}

	public void setCatalogType(String catalogType) {
		this.catalogType = catalogType;
	}

	public String getCatalogDataBase() {
		return catalogDataBase;
	}

	public void setCatalogDataBase(String catalogDataBase) {
		this.catalogDataBase = catalogDataBase;
	}

	public String getCatalogConnectionUri() {
		return catalogConnectionUri;
	}

	public void setCatalogConnectionUri(String catalogConnectionUri) {
		this.catalogConnectionUri = catalogConnectionUri;
	}

	public String getCatalogVersion() {
		return catalogVersion;
	}

	public void setCatalogVersion(String catalogVersion) {
		this.catalogVersion = catalogVersion;
	}

	public String getCatalogTable() {
		return catalogTable;
	}

	public void setCatalogTable(String catalogTable) {
		this.catalogTable = catalogTable;
	}

	public boolean isCatalog() {
		return isCatalog;
	}

	public void setCatalog(boolean catalog) {
		isCatalog = catalog;
	}

	public BaseNode parseFromJSONObject(JSONObject jsonObject) throws Exception{
		super.parseFromJSONObject(jsonObject);
		JSONObject exampleMeta = jsonObject.getJSONObject("example_meta");
		this.setBatchUri(exampleMeta.getString("batch_uri"));
		this.setStreamUri(exampleMeta.getString("stream_uri"));
		this.setDataFormat(exampleMeta.getString("data_format"));
		JSONArray fieldArray = exampleMeta.getJSONArray("name_list");
		if(null != fieldArray){
			String[] fieldNames = fieldArray.toJavaList(String.class).toArray(new String[0]);
			this.setFieldNames(fieldNames);
		}

		JSONArray typeArray = exampleMeta.getJSONArray("type_list");
		if(null != typeArray){
			String[] types = typeArray.toJavaList(String.class).toArray(new String[0]);
			this.setDataTypes(types);
		}
		if(null != fieldArray && null != typeArray) {
			if (fieldArray.size() != typeArray.size()) {
				throw new Exception(String.format("name_list length != type_list length: %d != %d",
						fieldArray.size(), typeArray.size()));
			}
		}
		boolean isSource = jsonObject.getBoolean("is_source");

		this.setSource(isSource);

		JSONObject batchArgs = jsonObject.getJSONObject("execute_properties").getJSONObject("batch_properties");
		for(String key: batchArgs.keySet()){
			this.batchArgs.put(key, batchArgs.getString(key));
		}
		JSONObject streamArgs = jsonObject.getJSONObject("execute_properties").getJSONObject("stream_properties");
		for(String key: streamArgs.keySet()){
			this.streamArgs.put(key, streamArgs.getString(key));
		}

		this.setCatalogName(exampleMeta.getString("catalog_name"));
		this.setCatalogDataBase(exampleMeta.getString("catalog_database"));
		this.setCatalogConnectionUri(exampleMeta.getString("catalog_connection_uri"));
		this.setCatalogType(exampleMeta.getString("catalog_type"));
		this.setCatalogVersion(exampleMeta.getString("catalog_version"));
		this.setCatalogTable(exampleMeta.getString("catalog_table"));
		if (this.getCatalogConnectionUri() != null) {
			this.setCatalog(true);
		}

		return this;
	}

	public Map<String, String> getBatchArgs() {
		return batchArgs;
	}

	public void setBatchArgs(Map<String, String> batchArgs) {
		this.batchArgs = batchArgs;
	}

	public Map<String, String> getStreamArgs() {
		return streamArgs;
	}

	public void setStreamArgs(Map<String, String> streamArgs) {
		this.streamArgs = streamArgs;
	}
}
