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
import com.apache.flink.ai.flow.node.meta.ModelMeta;
import com.apache.flink.ai.flow.node.meta.ModelVersionMeta;

import java.util.Map;

/**
 * predictor node description
 */
public class PredictorNode extends TransformerNode {

    private ModelMeta modelMeta;
    private ModelVersionMeta modelVersionMeta;

    public BaseNode parseFromJSONObject(JSONObject jsonObject) throws Exception {
        super.parseFromJSONObject(jsonObject);
        ModelMeta modelMeta = new ModelMeta();
        JSONObject model = jsonObject.getJSONObject("model");
        if (model != null) {
            modelMeta.setName(model.getString("name"));
            modelMeta.setDescription(model.getString("description"));
            modelMeta.setCreateTime(model.getLongValue("create_time"));
            modelMeta.setUpdateTime(model.getLongValue("update_time"));
            JSONObject modelProp = model.getJSONObject("properties");
            if (null != modelProp) {
                for (Map.Entry<String, Object> entry : modelProp.entrySet()) {
                    modelMeta.getProperties().put(entry.getKey(), (String) entry.getValue());
                }
            }
            this.setModelMeta(modelMeta);
        }
        JSONObject modelVersion = jsonObject.getJSONObject("model_version");
        if (modelVersion != null) {
            ModelVersionMeta modelVersionMeta = new ModelVersionMeta();
            modelVersionMeta.setVersion(modelVersion.getString("version"));
            modelVersionMeta.setVersionUri(modelVersion.getString("model_path"));
            modelVersionMeta.setMetricUri(modelVersion.getString("model_metric"));
            modelVersionMeta.setCreateTime(modelVersion.getLongValue("create_time"));
            modelVersionMeta.setSignature(modelVersion.getString("signature"));
            JSONObject modelVersionProp = modelVersion.getJSONObject("properties");
            if (null != modelVersionProp) {
                for (Map.Entry<String, Object> entry : modelVersionProp.entrySet()) {
                    modelVersionMeta.getProperties().put(entry.getKey(), (String) entry.getValue());
                }
            }
            this.setModelVersionMeta(modelVersionMeta);
        }
        return this;
    }

    public ModelMeta getModelMeta() {
        return modelMeta;
    }

    public void setModelMeta(ModelMeta modelMeta) {
        this.modelMeta = modelMeta;
    }

    public ModelVersionMeta getModelVersionMeta() {
        return modelVersionMeta;
    }

    public void setModelVersionMeta(ModelVersionMeta modelVersionMeta) {
        this.modelVersionMeta = modelVersionMeta;
    }
}
