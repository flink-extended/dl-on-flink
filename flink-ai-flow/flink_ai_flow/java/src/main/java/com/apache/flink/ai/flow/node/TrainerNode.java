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

import java.util.Map;

/**
 * predictor node description
 */
public class TrainerNode extends TransformerNode {

    private ModelMeta outputModelMeta;
    private ModelMeta baseModelMeta;

    public BaseNode parseFromJSONObject(JSONObject jsonObject) throws Exception {
        super.parseFromJSONObject(jsonObject);
        JSONObject model = jsonObject.getJSONObject("output_model");
        ModelMeta modelMeta;
        if (model != null) {
            modelMeta = parseModelMeta(model);
            this.setOutputModelMeta(modelMeta);
        }
        model = jsonObject.getJSONObject("from_model_version");
        if (model != null) {
            modelMeta = parseModelMeta(model);
            this.setBaseModelMeta(modelMeta);
        }
        return this;
    }

    private ModelMeta parseModelMeta(JSONObject model) {
        ModelMeta modelMeta = new ModelMeta();
        modelMeta.setName(model.getString("name"));
        modelMeta.setDescription(model.getString("description"));
        modelMeta.setProjectId(model.getLong("project_id"));
        modelMeta.setCreateTime(model.getLongValue("create_time"));
        modelMeta.setUpdateTime(model.getLongValue("update_time"));
        JSONObject modelProp = model.getJSONObject("properties");
        if (null != modelProp) {
            for (Map.Entry<String, Object> entry : modelProp.entrySet()) {
                modelMeta.getProperties().put(entry.getKey(), (String) entry.getValue());
            }
        }
        return modelMeta;
    }

    public ModelMeta getOutputModelMeta() {
        return outputModelMeta;
    }

    public void setOutputModelMeta(ModelMeta outputModelMeta) {
        this.outputModelMeta = outputModelMeta;
    }

    public ModelMeta getBaseModelMeta() {
        return baseModelMeta;
    }

    public void setBaseModelMeta(ModelMeta baseModelMeta) {
        this.baseModelMeta = baseModelMeta;
    }
}