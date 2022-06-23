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

package org.flinkextended.flink.ml.operator.ops;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.data.DataExchange;
import org.flinkextended.flink.ml.operator.util.ColumnInfos;
import org.flinkextended.flink.ml.operator.util.PythonFileUtil;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.iteration.IterationListener;
import org.apache.flink.streaming.api.operators.AbstractStreamOperator;
import org.apache.flink.streaming.api.operators.OneInputStreamOperator;
import org.apache.flink.streaming.api.operators.Output;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.types.Row;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import com.google.common.annotations.VisibleForTesting;

import java.io.IOException;
import java.io.InterruptedIOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

/**
 * A Flink operator that runs node of the deep learning cluster.
 *
 * @param <OUT> The output type of the operator.
 */
public class NodeOperator<OUT> extends AbstractStreamOperator<OUT>
        implements OneInputStreamOperator<Row, OUT>, IterationListener<OUT> {

    protected long closeTimeoutMs = 30_000;

    private final String nodeType;
    private final ClusterConfig clusterConfig;
    private final Configuration flinkConfig;
    private MLContext mlContext;
    private DataExchange<Row, OUT> dataExchange;
    private FutureTask<Void> serverFuture;
    private FutureTask<Void> dataExchangeConsumerFuture;
    private Thread serverThread;
    private Thread dataExchangeConsumerThread;

    public NodeOperator(String nodeType, ClusterConfig clusterConfig) {
        this(nodeType, clusterConfig, new Configuration());
    }

    public NodeOperator(String nodeType, ClusterConfig clusterConfig, Configuration flinkConfig) {
        this.nodeType = nodeType;
        this.clusterConfig = clusterConfig;
        this.flinkConfig = flinkConfig;
    }

    @Override
    public void open() throws Exception {
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(clusterConfig, flinkConfig);
        pythonEnvironmentManager.open(getRuntimeContext());

        Map<String, String> properties = new HashMap<>(clusterConfig.getProperties());
        properties.put(MLConstants.GPU_INFO, ResourcesUtils.parseGpuInfo(getRuntimeContext()));
        properties.putAll(pythonEnvironmentManager.getPythonEnvProperties());

        mlContext =
                new MLContext(
                        ExecutionMode.OTHER,
                        nodeType,
                        getRuntimeContext().getIndexOfThisSubtask(),
                        clusterConfig.getNodeTypeCntMap(),
                        clusterConfig.getEntryFuncName(),
                        properties,
                        clusterConfig.getPythonVirtualEnvZipPath(),
                        ColumnInfos.dummy().getNameToTypeMap());
        preparePythonFiles();

        Runnable nodeServerRunnable = createNodeServerRunnable();
        serverFuture = new FutureTask<>(nodeServerRunnable, null);
        serverThread = runRunnable(serverFuture, "NodeServer_" + maybeGetIdentity());

        dataExchange = new DataExchange<>(mlContext);
        DataExchangeConsumer<Row, OUT> dataExchangeConsumer =
                new DataExchangeConsumer<>(dataExchange, output);
        dataExchangeConsumerFuture = new FutureTask<>(dataExchangeConsumer, null);
        dataExchangeConsumerThread =
                runRunnable(
                        dataExchangeConsumerFuture,
                        "NodeServerDataExchangeConsumer_" + maybeGetIdentity());
    }

    @Override
    public void processElement(StreamRecord<Row> element) throws Exception {
        // put the read & write in a loop to avoid deadlock between write queue and read queue.
        boolean writeSuccess;
        try {
            do {
                writeSuccess = dataExchange.write(element.getValue());
                if (!writeSuccess) {
                    Thread.yield();
                }
            } while (!writeSuccess);
        } catch (IOException e) {
            if (!serverFuture.isDone()) {
                throw e;
            }
            // ignore
        }
    }

    @Override
    public void finish() throws Exception {
        LOG.info("Start finishing NodeOperator {}", maybeGetIdentity());
        cleanup(false);
    }

    @Override
    public void close() throws Exception {
        LOG.info("Start closing NodeOperator {}", maybeGetIdentity());
        cleanup(true);
        if (mlContext != null) {
            try {
                mlContext.close();
            } catch (IOException e) {
                LOG.error("Fail to close mlContext.", e);
            }
            mlContext = null;
        }
    }

    private void cleanup(boolean withTimeout) {
        if (mlContext != null && mlContext.getOutputQueue() != null) {
            mlContext.getOutputQueue().markFinished();
        }

        try {
            if (serverFuture != null && !serverFuture.isCancelled()) {
                if (withTimeout) {
                    serverFuture.get(closeTimeoutMs, TimeUnit.MILLISECONDS);
                } else {
                    serverFuture.get();
                }
            }
            if (dataExchangeConsumerFuture != null && !dataExchangeConsumerFuture.isCancelled()) {
                dataExchangeConsumerFuture.get();
            }
        } catch (InterruptedException e) {
            LOG.warn("Fail to join node {}", maybeGetIdentity(), e);
        } catch (TimeoutException e) {
            LOG.warn("Timeout waiting for node {} to finish", maybeGetIdentity(), e);
        } catch (ExecutionException e) {
            LOG.error(maybeGetIdentity() + " node server failed");
            throw new RuntimeException(e);
        } finally {
            if (serverFuture != null) {
                serverFuture.cancel(true);
                while (true) {
                    try {
                        serverThread.join(30_000);
                        if (serverThread.isAlive()) {
                            LOG.warn("NodeServer fail to exit in 30 second, interrupting...");
                            serverThread.interrupt();
                        } else {
                            break;
                        }
                    } catch (InterruptedException e) {
                        LOG.error("Fail to wait for NodeServer to exit", e);
                    }
                }
            }
            if (dataExchangeConsumerFuture != null) {
                while (true) {
                    dataExchangeConsumerFuture.cancel(true);
                    try {
                        dataExchangeConsumerThread.join();
                        break;
                    } catch (InterruptedException e) {
                        LOG.error("Fail to wait for DataExchangeConsumer to exit", e);
                    }
                }
            }
            serverFuture = null;
            dataExchangeConsumerFuture = null;

            LOG.info("Records output: " + dataExchange.getReadRecords());
        }
    }

    @Override
    public void onEpochWatermarkIncremented(
            int epochWatermark, Context context, Collector<OUT> collector) throws Exception {
        mlContext.getOutputQueue().markBarrier();
        while (!serverFuture.isDone() && mlContext.getOutputQueue().canRead()) {
            // We use sleep to avoid tight loop checking the python process consume
            // all the data in the queue. The time of sleep is trivial compared to
            // the time of training an epoch.
            Thread.sleep(100);
        }
        if (serverFuture.isDone()) {
            LOG.info("{} finished at epoch {}", maybeGetIdentity(), epochWatermark);
            return;
        }
        context.output(new OutputTag<Integer>("termination") {}, 0);
    }

    @Override
    public void onIterationTerminated(Context context, Collector<OUT> collector) throws Exception {}

    private Thread runRunnable(Runnable runnable, String threadName) throws IOException {
        try {
            Thread t = new Thread(runnable);
            t.setDaemon(true);
            t.setName(threadName);
            t.start();
            LOG.info("start: {}", threadName);
            return t;
        } catch (Exception e) {
            LOG.error("Fail to start node service.", e);
            throw new IOException(e.getMessage());
        }
    }

    public String getNodeType() {
        return nodeType;
    }

    @VisibleForTesting
    void preparePythonFiles() throws IOException {
        PythonFileUtil.preparePythonFilesForExec(getRuntimeContext(), mlContext);
    }

    @VisibleForTesting
    Runnable createNodeServerRunnable() {
        return new NodeServer(mlContext, nodeType);
    }

    @VisibleForTesting
    MLContext getMlContext() {
        return mlContext;
    }

    @VisibleForTesting
    FutureTask<Void> getServerFuture() {
        return serverFuture;
    }

    @VisibleForTesting
    DataExchange<Row, OUT> getDataExchange() {
        return dataExchange;
    }

    @VisibleForTesting
    FutureTask<Void> getDataExchangeConsumerFuture() {
        return dataExchangeConsumerFuture;
    }

    private String maybeGetIdentity() {
        if (mlContext == null) {
            return "";
        }
        return mlContext.getIdentity();
    }

    private static class DataExchangeConsumer<IN, OUT> implements Runnable {
        private final DataExchange<IN, OUT> dataExchange;
        private final Output<StreamRecord<OUT>> output;

        DataExchangeConsumer(DataExchange<IN, OUT> dataExchange, Output<StreamRecord<OUT>> output) {
            this.dataExchange = dataExchange;
            this.output = output;
        }

        @Override
        public void run() {
            while (true) {
                try {
                    OUT r = dataExchange.read(true);
                    if (r != null) {
                        output.collect(new StreamRecord<>(r));
                    } else {
                        break;
                    }
                } catch (InterruptedIOException e) {
                    LOG.warn("Reading from data exchange is interrupted.", e);
                    break;
                } catch (IOException e) {
                    LOG.error("Fail to read data from python.", e);
                }
            }

            LOG.info("DataExchange consumer consume all data, exiting...");
        }
    }
}
