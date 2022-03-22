/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.tensorflow.client;

import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.role.BaseRole;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

class TestTFConfig extends TFConfigBase {

    public TestTFConfig(
            int workerNum,
            int psNum,
            Map<String, String> properties,
            String pythonFile,
            String funName,
            String envPath) {
        super(workerNum, psNum, properties, pythonFile, funName, envPath);
    }

    public TestTFConfig(
            int workerNum,
            int psNum,
            Map<String, String> properties,
            String[] pythonFiles,
            String funName,
            String envPath) {
        super(workerNum, psNum, properties, pythonFiles, funName, envPath);
    }

    @Override
    public FlatMapFunction getInferenceFlatMapFunction(
            BaseRole role,
            MLConfig mlConfig,
            TypeInformation inTypeInfo,
            TypeInformation outTypeInfo) {
        return null;
    }

    @Override
    public TFConfigBase deepCopy() {
        String[] pyFiles =
                Arrays.copyOf(
                        this.mlConfig.getPythonFiles(), this.mlConfig.getPythonFiles().length);
        HashMap<String, String> destProperties = new HashMap<>(this.getMlConfig().getProperties());
        return new TestTFConfig(
                getWorkerNum(),
                getPsNum(),
                destProperties,
                pyFiles,
                String.copyValueOf(getFuncName().toCharArray()),
                this.mlConfig.getEnvPath());
    }
}
