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

package org.flinkextended.flink.ml.examples.tensorflow.mnist;

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.python.ProcessPythonRunner;
import org.flinkextended.flink.ml.tensorflow.client.TFConfig;
import org.flinkextended.flink.ml.tensorflow.client.TFConfigBase;
import org.flinkextended.flink.ml.util.HttpUtil;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.PythonUtil;
import org.flinkextended.flink.ml.util.ShellExec;
import org.flinkextended.flink.ml.util.SysUtil;

import com.google.common.base.Preconditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** prepare mnist data to run tensorflow distribute program. */
public class MnistDataUtil {

    public static final String DATA_ADDRESS =
            "https://raw.githubusercontent.com/wuchaochen/testdata/master/mnist/";
    public static final String TRAIN_IMAGES = "train-images-idx3-ubyte.gz";
    public static final String TRAIN_LABELS = "train-labels-idx1-ubyte.gz";
    public static final String T_10_K_IMAGES = "t10k-images-idx3-ubyte.gz";
    public static final String T_10_K_LABELS = "t10k-labels-idx1-ubyte.gz";
    public static final String DATA_DIR = "/dl-on-flink-examples/target/data/";
    private static final Logger LOG = LoggerFactory.getLogger(MnistDataUtil.class);

    private static String getDataPath() {
        String rootPath = SysUtil.getProjectRootPath();
        return rootPath + DATA_DIR;
    }

    /**
     * download mnist data to local address.
     *
     * @return mnist test data path.
     */
    public static String downloadData() {
        String dataPath = getDataPath();
        File dataFile = new File(dataPath);
        Preconditions.checkState(
                dataFile.exists() || dataFile.mkdirs(),
                "Failed to create " + dataFile.getAbsolutePath());
        File trainImagesFile = new File(dataPath + TRAIN_IMAGES);
        if (!trainImagesFile.exists()) {
            System.out.println("download:" + TRAIN_IMAGES);
            HttpUtil.httpDownload(DATA_ADDRESS + TRAIN_IMAGES, dataPath + TRAIN_IMAGES);
        }
        File trainLablesFile = new File(dataPath + TRAIN_LABELS);
        if (!trainLablesFile.exists()) {
            System.out.println("download:" + TRAIN_LABELS);
            HttpUtil.httpDownload(DATA_ADDRESS + TRAIN_LABELS, dataPath + TRAIN_LABELS);
        }
        File t10KImagesFile = new File(dataPath + T_10_K_IMAGES);
        if (!t10KImagesFile.exists()) {
            System.out.println("download:" + T_10_K_IMAGES);
            HttpUtil.httpDownload(DATA_ADDRESS + T_10_K_IMAGES, dataPath + T_10_K_IMAGES);
        }
        File t10KLabelsFile = new File(dataPath + T_10_K_LABELS);
        if (!t10KLabelsFile.exists()) {
            System.out.println("download:" + T_10_K_LABELS);
            HttpUtil.httpDownload(DATA_ADDRESS + T_10_K_LABELS, dataPath + T_10_K_LABELS);
        }
        return dataPath;
    }

    /**
     * convert mnist original test data to tensorflow record.
     *
     * @throws IOException
     */
    private static void genTFRecord() throws IOException {
        String dataPath = getDataPath();
        File trainDataFile = new File(dataPath + "train");
        boolean flag = false;
        if (!trainDataFile.exists()) {
            trainDataFile.mkdirs();
            flag = true;
        }
        File testDataFile = new File(dataPath + "test");
        if (!testDataFile.exists()) {
            testDataFile.mkdirs();
            flag = true;
        }
        String rootPath = SysUtil.getProjectRootPath();
        File f = new File(rootPath + "/dl-on-flink-examples/src/test/python/mnist_data_setup.py");
        System.out.println(f.getAbsolutePath());
        if (flag) {
            TFConfigBase config = new TFConfig(0, 0, null, (String) null, null, null);
            MLContext mlContext =
                    new MLContext(
                            ExecutionMode.TRAIN, config.getMlConfig(), "worker", 0, null, null);
            runMnistSetup(mlContext, f.getAbsolutePath(), getDataPath(), getDataPath(), 2);
        }
    }

    public static void prepareData() throws IOException {
        genTFRecord();
    }

    public static void main(String[] args) throws IOException {
        genTFRecord();
    }

    static void runMnistSetup(
            MLContext mlContext, String script, String input, String output, int partitions)
            throws IOException {
        List<String> args = new ArrayList<>();
        args.add("python");
        args.add(script);
        args.add(input);
        args.add(output);
        args.add(String.valueOf(partitions));
        ProcessBuilder builder = new ProcessBuilder(args);
        PythonUtil.setupVirtualEnvProcess(mlContext, builder);
        String classPath = ProcessPythonRunner.getClassPath();
        if (classPath != null) {
            builder.environment().put(MLConstants.CLASSPATH, classPath);
        }
        Process child = builder.start();
        Thread inLogger =
                new Thread(
                        new ShellExec.ProcessLogger(
                                child.getInputStream(), new ShellExec.StdOutConsumer()));
        Thread errLogger =
                new Thread(
                        new ShellExec.ProcessLogger(
                                child.getErrorStream(), new ShellExec.StdOutConsumer()));
        inLogger.setName(mlContext.getIdentity() + "-in-logger");
        inLogger.setDaemon(true);
        errLogger.setName(mlContext.getIdentity() + "-err-logger");
        errLogger.setDaemon(true);
        inLogger.start();
        errLogger.start();
        try {
            int r = child.waitFor();
            inLogger.join();
            errLogger.join();
            if (r != 0) {
                throw new RuntimeException("Mnist data setup returned with code " + r);
            }
        } catch (InterruptedException e) {
            LOG.warn("Mnist data setup interrupted", e);
        } finally {
            child.destroyForcibly();
        }
    }
}
