/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
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
import org.flinkextended.flink.ml.cluster.role.PsRole;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import com.google.common.base.Preconditions;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/** tensorflow cluster configuration, TFConfig is a type of MLConfig. */
public abstract class TFConfigBase implements Serializable {
    private static final Logger LOG = LoggerFactory.getLogger(TFConfigBase.class);
    protected MLConfig mlConfig;

    /**
     * Construct a TFConfig.
     *
     * @param workerNum the number of TF workers
     * @param psNum the number of TF PS
     * @param properties TF properties
     * @param pythonFile the python file, the entry python file
     * @param funName the entry function name in the first python file
     */
    public TFConfigBase(
            int workerNum,
            int psNum,
            Map<String, String> properties,
            String pythonFile,
            String funName,
            String envPath) {
        this(
                workerNum,
                psNum,
                properties,
                StringUtils.isEmpty(pythonFile) ? null : new String[] {pythonFile},
                funName,
                envPath);
    }

    /**
     * Construct a TFConfig.
     *
     * @param workerNum the number of TF workers
     * @param psNum the number of TF PS
     * @param properties TF properties
     * @param pythonFiles the python files, the first one will be the entry python file
     * @param funName the entry function name in the first python file
     */
    public TFConfigBase(
            int workerNum,
            int psNum,
            Map<String, String> properties,
            String[] pythonFiles,
            String funName,
            String envPath) {
        Preconditions.checkArgument(workerNum >= 0);
        Preconditions.checkArgument(psNum >= 0);
        Map<String, Integer> jobNum = new HashMap<>();
        jobNum.put(new WorkerRole().name(), workerNum);
        jobNum.put(new PsRole().name(), psNum);
        this.mlConfig = new MLConfig(jobNum, properties, pythonFiles, funName, envPath);
        if (!this.getMlConfig().getProperties().containsKey(MLConstants.JOB_VERSION)) {
            this.getMlConfig()
                    .getProperties()
                    .put(MLConstants.JOB_VERSION, String.valueOf(System.currentTimeMillis()));
        }
        loadSystemConfig();
    }

    public abstract FlatMapFunction getInferenceFlatMapFunction(
            BaseRole role,
            MLConfig mlConfig,
            TypeInformation inTypeInfo,
            TypeInformation outTypeInfo);

    /**
     * virtual environment getter.
     *
     * @return virtual environment address.
     */
    public String getEnvPath() {
        return mlConfig.getEnvPath();
    }

    /**
     * python scripts getter.
     *
     * @return python script list.
     */
    public String[] getPythonFiles() {
        return mlConfig.getPythonFiles();
    }

    /**
     * tensorflow cluster worker number getter.
     *
     * @return worker number.
     */
    public int getWorkerNum() {
        return mlConfig.getRoleParallelismMap().get(new WorkerRole().name());
    }

    /**
     * tensorflow cluster ps number getter.
     *
     * @return ps number.
     */
    public int getPsNum() {
        return mlConfig.getRoleParallelismMap().get(new PsRole().name());
    }

    /**
     * tensorflow cluster configuration properties getter.
     *
     * @return configuration properties.
     */
    public Map<String, String> getProperties() {
        return getMlConfig().getProperties();
    }

    /**
     * python script entry function getter.
     *
     * @return python script entry function name.
     */
    public String getFuncName() {
        return mlConfig.getFuncName();
    }

    /**
     * @param key
     * @param value
     */
    public void addProperty(String key, String value) {
        getMlConfig().getProperties().put(key, value);
    }

    /**
     * @param key
     * @return
     */
    public String getProperty(String key) {
        return getMlConfig().getProperties().get(key);
    }

    /**
     * @param key
     * @param defaultVal
     * @return
     */
    public String getProperty(String key, String defaultVal) {
        String val = getMlConfig().getProperties().get(key);
        if (val == null) {
            return defaultVal;
        }
        return val;
    }

    /**
     * tensorflow cluster worker number setter.
     *
     * @param workerNum worker number.
     */
    public void setWorkerNum(int workerNum) {
        this.mlConfig.getRoleParallelismMap().put(new WorkerRole().name(), workerNum);
    }

    /**
     * tensorflow cluster ps number setter.
     *
     * @param psNum ps number.
     */
    public void setPsNum(int psNum) {
        this.mlConfig.getRoleParallelismMap().put(new PsRole().name(), psNum);
    }

    /**
     * tensorflow python scripts setter.
     *
     * @param pythonFiles python scripts.
     */
    public void setPythonFiles(String[] pythonFiles) {
        this.mlConfig.setPythonFiles(pythonFiles);
    }

    public abstract TFConfigBase deepCopy();

    @Override
    public String toString() {
        return "TFConfig{"
                + "envPath='"
                + getEnvPath()
                + '\''
                + ", pythonFiles="
                + Arrays.toString(getPythonFiles())
                + ", funcName='"
                + getFuncName()
                + '\''
                + ", workerNum="
                + getWorkerNum()
                + ", psNum="
                + getPsNum()
                + ", properties="
                + getMlConfig().getProperties()
                + '}';
    }

    private void loadSystemConfig() {
        Configuration configuration = new Configuration();
        configuration.addResource(MLConstants.CONFIG_TENSORFLOW_FLINK);
        for (Map.Entry<String, String> entry : configuration) {
            if (!getMlConfig().getProperties().containsKey(entry.getKey())) {
                getMlConfig().getProperties().put(entry.getKey(), entry.getValue());
            }
        }
    }

    /**
     * @return true: tensorflow worker 0 plan as a cluster role, false: worker 0 plan as a node of
     *     worker role.
     */
    public boolean isWorkerZeroAlone() {
        return Boolean.valueOf(
                this.getProperties().getOrDefault(TFConstants.TF_IS_CHIEF_ALONE, "false"));
    }

    public boolean isChiefRole() {
        return Boolean.valueOf(
                this.getProperties().getOrDefault(TFConstants.TF_IS_CHIEF_ROLE, "false"));
    }

    /**
     * machine learning configuration getter.
     *
     * @return machine learning configuration.
     */
    public MLConfig getMlConfig() {
        return mlConfig;
    }
}
