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
package org.aiflow.client.common;

import org.aiflow.client.proto.Message.ModelVersionStage;

public enum ModelStage {
    GENERATED(ModelVersionStage.GENERATED),
    VALIDATED(ModelVersionStage.VALIDATED),
    DEPLOYED(ModelVersionStage.DEPLOYED),
    DEPRECATED(ModelVersionStage.DEPRECATED),
    DELETED(ModelVersionStage.DELETED);

    private ModelVersionStage modelStage;

    ModelStage(ModelVersionStage modelStage) {
        this.modelStage = modelStage;
    }

    public ModelVersionStage getModelStage() {
        return modelStage;
    }

    public static ModelStage getModelStage(ModelVersionStage modelStage) {
        for (ModelStage stage : ModelStage.values()) {
            if (stage.getModelStage() == modelStage) {
                return stage;
            }
        }
        return null;
    }
}
