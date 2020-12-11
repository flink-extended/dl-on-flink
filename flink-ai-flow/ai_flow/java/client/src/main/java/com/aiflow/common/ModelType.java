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
package com.aiflow.common;

import com.aiflow.proto.Message;

public enum ModelType {

    CHECKPOINT(Message.ModelType.CHECKPOINT),
    SAVED_MODEL(Message.ModelType.SAVED_MODEL),
    H5(Message.ModelType.H5);

    private Message.ModelType modelType;

    ModelType(Message.ModelType modelType) {
        this.modelType = modelType;
    }

    public Message.ModelType getModelType() {
        return modelType;
    }

    public static ModelType getModelType(Message.ModelType modelType) {
        for(ModelType type: ModelType.values()) {
            if(type.getModelType() == modelType) {
                return type;
            }
        }
        return null;
    }
}