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
package com.aiflow.entity;

import com.aiflow.common.ExecutionType;
import com.aiflow.proto.Message;
import com.aiflow.proto.Message.SchemaProto;
import com.aiflow.proto.MetadataServiceOuterClass;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static com.aiflow.entity.Schema.buildSchema;
import static com.aiflow.util.Transform.*;

public class DatasetMeta {

    private Long uuid;
    private String name;
    private String dataFormat;
    private String description;
    private String uri;
    private Long createTime;
    private Long updateTime;
    private Map<String, String> properties;
    private Schema schema;
    private String catalogName;
    private String catalogType;
    private String catalogDatabase;
    private String catalogConnectionUri;
    private String catalogTable;

    public DatasetMeta() {
    }

    public DatasetMeta(String name, String dataFormat, String description, String uri, Long createTime, Long updateTime, Map<String, String> properties, Schema schema, String catalogName, String catalogType, String catalogDatabase, String catalogConnectionUri, String catalogTable) {
        this.name = name;
        this.dataFormat = dataFormat;
        this.description = description;
        this.uri = uri;
        this.createTime = createTime;
        this.updateTime = updateTime;
        this.properties = properties;
        this.schema = schema;
        this.catalogName = catalogName;
        this.catalogType = catalogType;
        this.catalogDatabase = catalogDatabase;
        this.catalogConnectionUri = catalogConnectionUri;
        this.catalogTable = catalogTable;
    }

    public DatasetMeta(Long uuid, String name, String dataFormat, String description, String uri, Long createTime, Long updateTime, Map<String, String> properties, Schema schema, String catalogName, String catalogType, String catalogDatabase, String catalogConnectionUri, String catalogTable) {
        this(name, dataFormat, description, uri, createTime, updateTime, properties, schema, catalogName, catalogType, catalogDatabase, catalogConnectionUri, catalogTable);
        this.uuid = uuid;
    }

    public Long getUuid() {
        return uuid;
    }

    public void setUuid(Long uuid) {
        this.uuid = uuid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDataFormat() {
        return dataFormat;
    }

    public void setDataFormat(String dataFormat) {
        this.dataFormat = dataFormat;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getUri() {
        return uri;
    }

    public void setUri(String uri) {
        this.uri = uri;
    }

    public Long getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Long createTime) {
        this.createTime = createTime;
    }

    public Long getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Long updateTime) {
        this.updateTime = updateTime;
    }

    public Map<String, String> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, String> properties) {
        this.properties = properties;
    }

    public Schema getSchema() {
        return schema;
    }

    public void setSchema(Schema schema) {
        this.schema = schema;
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

    public String getCatalogDatabase() {
        return catalogDatabase;
    }

    public void setCatalogDatabase(String catalogDatabase) {
        this.catalogDatabase = catalogDatabase;
    }

    public String getCatalogConnectionUri() {
        return catalogConnectionUri;
    }

    public void setCatalogConnectionUri(String catalogConnectionUri) {
        this.catalogConnectionUri = catalogConnectionUri;
    }

    public String getCatalogTable() {
        return catalogTable;
    }

    public void setCatalogTable(String catalogTable) {
        this.catalogTable = catalogTable;
    }

    @Override
    public String toString() {
        return "DatasetMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", dataFormat='" + dataFormat + '\'' +
                ", description='" + description + '\'' +
                ", uri='" + uri + '\'' +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                ", properties=" + properties +
                ", schema=" + schema +
                ", catalogName='" + catalogName + '\'' +
                ", catalogType='" + catalogType + '\'' +
                ", catalogDatabase='" + catalogDatabase + '\'' +
                ", catalogConnectionUri='" + catalogConnectionUri + '\'' +
                ", catalogTable='" + catalogTable + '\'' +
                '}';
    }

    public static DatasetMeta buildDatasetMeta(Message.DatasetProto datasetProto) {
        return datasetProto == null ? null : new DatasetMeta(datasetProto.getUuid(),
                datasetProto.getName(),
                datasetProto.getDataFormat().getValue(),
                datasetProto.getDescription().getValue(),
                datasetProto.getUri().getValue(),
                datasetProto.getCreateTime().getValue(),
                datasetProto.getUpdateTime().getValue(),
                datasetProto.getPropertiesMap(),
                buildSchema(datasetProto.getSchema()),
                datasetProto.getCatalogName().getValue(),
                datasetProto.getCatalogType().getValue(),
                datasetProto.getCatalogDatabase().getValue(),
                datasetProto.getCatalogConnectionUri().getValue(),
                datasetProto.getCatalogTable().getValue());
    }

    public static List<DatasetMeta> buildDatasetMetas(MetadataServiceOuterClass.DatasetListProto datasetListProto) {
        if (datasetListProto == null) {
            return null;
        } else {
            List<DatasetMeta> datasetMetas = new ArrayList<>();
            for (Message.DatasetProto datasetProto : datasetListProto.getDatasetsList()) {
                datasetMetas.add(buildDatasetMeta(datasetProto));
            }
            return datasetMetas;
        }
    }

    public static List<Message.DatasetProto> buildDatasetProtos(List<DatasetMeta> datasetMetas) {
        List<Message.DatasetProto> datasetProtos = new ArrayList<>();
        for (DatasetMeta datasetMeta : datasetMetas) {
            Message.DatasetProto.Builder builder = Message.DatasetProto.newBuilder().setName(datasetMeta.getName())
                    .setDataFormat(stringValue(datasetMeta.getDataFormat())).setDescription(stringValue(datasetMeta.getDescription()))
                    .setUri(stringValue(datasetMeta.getUri()))
                    .setCreateTime(int64Value(datasetMeta.getCreateTime())).setUpdateTime(int64Value(datasetMeta.getUpdateTime()))
                    .putAllProperties(datasetMeta.getProperties()).setCatalogName(stringValue(datasetMeta.getCatalogName()))
                    .setCatalogType(stringValue(datasetMeta.getCatalogType())).setCatalogDatabase(stringValue(datasetMeta.getCatalogDatabase()))
                    .setCatalogConnectionUri(stringValue(datasetMeta.getCatalogConnectionUri()))
                    .setCatalogTable(stringValue(datasetMeta.getCatalogTable()));
            if (datasetMeta.getSchema() != null) {
                builder.setSchema(SchemaProto.newBuilder().addAllNameList(datasetMeta.getSchema().getNameList()).addAllTypeList(dataTypeList(datasetMeta.getSchema().getTypeList())));
            }
            datasetProtos.add(builder.build());
        }
        return datasetProtos;
    }
}