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
import com.aiflow.proto.Message.ExampleProto;
import com.aiflow.proto.Message.SchemaProto;
import com.aiflow.proto.MetadataServiceOuterClass.ExampleListProto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static com.aiflow.entity.Schema.buildSchema;
import static com.aiflow.util.Transform.*;

public class ExampleMeta {

    private Long uuid;
    private String name;
    private ExecutionType supportType;
    private String dataFormat;
    private String description;
    private String batchUri;
    private String streamUri;
    private Long createTime;
    private Long updateTime;
    private Map<String, String> properties;
    private Schema schema;
    private String catalogName;
    private String catalogType;
    private String catalogDatabase;
    private String catalogConnectionUri;
    private String catalogVersion;
    private String catalogTable;

    public ExampleMeta() {
    }

    public ExampleMeta(String name, ExecutionType supportType, String dataFormat, String description, String batchUri, String streamUri, Long createTime, Long updateTime, Map<String, String> properties, Schema schema, String catalogName, String catalogType, String catalogDatabase, String catalogConnectionUri, String catalogVersion, String catalogTable) {
        this.name = name;
        this.supportType = supportType;
        this.dataFormat = dataFormat;
        this.description = description;
        this.batchUri = batchUri;
        this.streamUri = streamUri;
        this.createTime = createTime;
        this.updateTime = updateTime;
        this.properties = properties;
        this.schema = schema;
        this.catalogName = catalogName;
        this.catalogType = catalogType;
        this.catalogDatabase = catalogDatabase;
        this.catalogConnectionUri = catalogConnectionUri;
        this.catalogVersion = catalogVersion;
        this.catalogTable = catalogTable;
    }

    public ExampleMeta(Long uuid, String name, ExecutionType supportType, String dataFormat, String description, String batchUri, String streamUri, Long createTime, Long updateTime, Map<String, String> properties, Schema schema, String catalogName, String catalogType, String catalogDatabase, String catalogConnectionUri, String catalogVersion, String catalogTable) {
        this(name, supportType, dataFormat, description, batchUri, streamUri, createTime, updateTime, properties, schema, catalogName, catalogType, catalogDatabase, catalogConnectionUri, catalogVersion, catalogTable);
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

    public ExecutionType getSupportType() {
        return supportType;
    }

    public void setSupportType(ExecutionType supportType) {
        this.supportType = supportType;
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

    @Override
    public String toString() {
        return "ExampleMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", supportType=" + supportType +
                ", dataFormat='" + dataFormat + '\'' +
                ", description='" + description + '\'' +
                ", batchUri='" + batchUri + '\'' +
                ", streamUri='" + streamUri + '\'' +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                ", properties=" + properties +
                ", schema=" + schema +
                ", catalogName='" + catalogName + '\'' +
                ", catalogType='" + catalogType + '\'' +
                ", catalogDatabase='" + catalogDatabase + '\'' +
                ", catalogConnectionUri='" + catalogConnectionUri + '\'' +
                ", catalogVersion='" + catalogVersion + '\'' +
                ", catalogTable='" + catalogTable + '\'' +
                '}';
    }

    public static ExampleMeta buildExampleMeta(ExampleProto exampleProto) {
        return exampleProto == null ? null : new ExampleMeta(exampleProto.getUuid(),
                exampleProto.getName(),
                ExecutionType.valueOf(exampleProto.getSupportType().name()),
                exampleProto.getDataFormat().getValue(),
                exampleProto.getDescription().getValue(),
                exampleProto.getBatchUri().getValue(),
                exampleProto.getStreamUri().getValue(),
                exampleProto.getCreateTime().getValue(),
                exampleProto.getUpdateTime().getValue(),
                exampleProto.getPropertiesMap(),
                buildSchema(exampleProto.getSchema()),
                exampleProto.getCatalogName().getValue(),
                exampleProto.getCatalogType().getValue(),
                exampleProto.getCatalogDatabase().getValue(),
                exampleProto.getCatalogConnectionUri().getValue(),
                exampleProto.getCatalogVersion().getValue(),
                exampleProto.getCatalogTable().getValue());
    }

    public static List<ExampleMeta> buildExampleMetas(ExampleListProto exampleListProto) {
        if (exampleListProto == null) {
            return null;
        } else {
            List<ExampleMeta> exampleMetas = new ArrayList<>();
            for (ExampleProto exampleProto : exampleListProto.getExamplesList()) {
                exampleMetas.add(buildExampleMeta(exampleProto));
            }
            return exampleMetas;
        }
    }

    public static List<ExampleProto> buildExampleProtos(List<ExampleMeta> exampleMetas) {
        List<ExampleProto> exampleProtos = new ArrayList<>();
        for (ExampleMeta exampleMeta : exampleMetas) {
            ExampleProto.Builder builder = ExampleProto.newBuilder().setName(exampleMeta.getName()).setSupportType(exampleMeta.getSupportType().getExecutionType())
                    .setDataFormat(stringValue(exampleMeta.getDataFormat())).setDescription(stringValue(exampleMeta.getDescription()))
                    .setBatchUri(stringValue(exampleMeta.getBatchUri())).setStreamUri(stringValue(exampleMeta.getStreamUri()))
                    .setCreateTime(int64Value(exampleMeta.getCreateTime())).setUpdateTime(int64Value(exampleMeta.getUpdateTime()))
                    .putAllProperties(exampleMeta.getProperties()).setCatalogName(stringValue(exampleMeta.getCatalogName()))
                    .setCatalogType(stringValue(exampleMeta.getCatalogType())).setCatalogDatabase(stringValue(exampleMeta.getCatalogDatabase()))
                    .setCatalogConnectionUri(stringValue(exampleMeta.getCatalogConnectionUri())).setCatalogVersion(stringValue(exampleMeta.getCatalogVersion()))
                    .setCatalogTable(stringValue(exampleMeta.getCatalogTable()));
            if (exampleMeta.getSchema() != null) {
                builder.setSchema(SchemaProto.newBuilder().addAllNameList(exampleMeta.getSchema().getNameList()).addAllTypeList(dataTypeList(exampleMeta.getSchema().getTypeList())));
            }
            exampleProtos.add(builder.build());
        }
        return exampleProtos;
    }
}