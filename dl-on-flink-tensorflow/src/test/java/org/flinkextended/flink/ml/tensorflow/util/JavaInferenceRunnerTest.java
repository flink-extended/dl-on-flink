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

package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.data.DataExchange;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;
import org.flinkextended.flink.ml.util.ShellExec;
import org.flinkextended.flink.ml.util.TestUtil;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.types.Row;
import org.apache.flink.types.RowKind;
import org.apache.flink.util.Preconditions;

import com.google.common.base.Joiner;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.mockito.internal.util.reflection.Whitebox;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.assertEquals;

public class JavaInferenceRunnerTest {
    private static final String rootPath =
            TestUtil.getProjectRootPath() + "/dl-on-flink-tensorflow";

    private FutureTask<Void> nodeFuture;

    private MLContext mlContext;
    private NodeServer nodeServer;

    @Before
    public void setUp() throws Exception {
        final Path tempDirectory = Files.createTempDirectory("");
        final Path modelPath = Paths.get(tempDirectory.toUri().getPath(), "model");
        mlContext = DummyContext.createDummyMLContext();
        Preconditions.checkState(
                ShellExec.run(
                        String.format(
                                "python %s %s",
                                rootPath + "/src/test/python/mnist_model.py",
                                modelPath.toUri().getPath())));

        mlContext
                .getProperties()
                .put(TFConstants.TF_INFERENCE_EXPORT_PATH, modelPath.toUri().getPath());
        mlContext.getProperties().put(TFConstants.TF_INFERENCE_INPUT_TENSOR_NAMES, "image");
        mlContext.getProperties().put(TFConstants.TF_INFERENCE_OUTPUT_TENSOR_NAMES, "prediction");
        mlContext
                .getProperties()
                .put(
                        TFConstants.TF_INFERENCE_OUTPUT_ROW_FIELDS,
                        Joiner.on(",").join(new String[] {"prediction"}));
        setExampleCodingType(mlContext);
        startNodeServer();
    }

    @After
    public void tearDown() throws Exception {
        nodeServer.setAmCommand(NodeServer.AMCommand.STOP);
        nodeFuture.get();
    }

    @Test
    public void testJavaInferenceRunner() throws Exception {
        while (nodeServer.getPort() == null) {
            Thread.sleep(1000);
        }
        final RowTypeInfo inRowType =
                new RowTypeInfo(
                        new TypeInformation[] {Types.PRIMITIVE_ARRAY(Types.FLOAT)},
                        new String[] {"image"});
        final RowTypeInfo outRowTpe =
                new RowTypeInfo(new TypeInformation[] {Types.LONG}, new String[] {"prediction"});
        final JavaInferenceRunner runner =
                new JavaInferenceRunner("localhost", nodeServer.getPort(), inRowType, outRowTpe);

        DataExchange<Row, Row> dataExchange =
                (DataExchange<Row, Row>) Whitebox.getInternalState(runner, "dataExchange");
        dataExchange = Mockito.spy(dataExchange);
        Whitebox.setInternalState(runner, "dataExchange", dataExchange);

        Mockito.when(dataExchange.read(Mockito.anyBoolean()))
                .thenAnswer(
                        new Answer<Row>() {
                            private int callCnt = 0;

                            @Override
                            public Row answer(InvocationOnMock invocation) throws Throwable {
                                if (callCnt > 0) {
                                    return null;
                                }
                                callCnt++;
                                final Row row = new Row(RowKind.INSERT, 1);
                                float[] floats = new float[784];
                                Arrays.fill(floats, 0.1f);
                                row.setField(0, floats);
                                return row;
                            }
                        });

        runner.run();

        ArgumentCaptor<Row> captor = ArgumentCaptor.forClass(Row.class);
        Mockito.verify(dataExchange).write(captor.capture());
        final Row row = captor.getValue();
        assertEquals(1, row.getArity());

        runner.close();
    }

    private void setExampleCodingType(MLContext mlContext) {
        mlContext
                .getProperties()
                .put(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getCanonicalName());
        mlContext
                .getProperties()
                .put(MLConstants.DECODING_CLASS, RowCSVCoding.class.getCanonicalName());
    }

    private FutureTask<Void> startNodeServer() throws MLException {
        nodeServer = new NodeServer(mlContext, "worker");
        nodeFuture = new FutureTask<>(nodeServer, null);
        Thread thread = new Thread(nodeFuture);
        thread.setDaemon(true);
        thread.start();
        return nodeFuture;
    }
}
