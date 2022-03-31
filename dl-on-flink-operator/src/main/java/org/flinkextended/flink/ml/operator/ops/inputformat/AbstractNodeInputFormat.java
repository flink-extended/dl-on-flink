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

package org.flinkextended.flink.ml.operator.ops.inputformat;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.data.DataExchange;
import org.flinkextended.flink.ml.operator.hook.FlinkOpHookManager;
import org.flinkextended.flink.ml.operator.util.PythonFileUtil;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.api.common.io.DefaultInputSplitAssigner;
import org.apache.flink.api.common.io.RichInputFormat;
import org.apache.flink.api.common.io.statistics.BaseStatistics;
import org.apache.flink.core.io.InputSplitAssigner;

import com.google.common.annotations.VisibleForTesting;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * An Abstract implementation of {@link RichInputFormat} that runs various node type of deep
 * learning cluster node.
 *
 * @param <OUT> The type of the produced records.
 */
public abstract class AbstractNodeInputFormat<OUT> extends RichInputFormat<OUT, NodeInputSplit> {
    private static final Logger LOG = LoggerFactory.getLogger(AbstractNodeInputFormat.class);

    protected final ClusterConfig clusterConfig;
    protected long closeTimeoutMs = 180_000;

    private MLContext mlContext;
    private FlinkOpHookManager hookManager;
    private DataExchange<OUT, OUT> dataExchange;
    private FutureTask<Void> serverFuture;
    private final AtomicBoolean isClose;

    public AbstractNodeInputFormat(ClusterConfig clusterConfig) {
        this.clusterConfig = clusterConfig;
        this.isClose = new AtomicBoolean(false);
    }

    @Override
    public InputSplitAssigner getInputSplitAssigner(NodeInputSplit[] inputSplits) {
        return new DefaultInputSplitAssigner(inputSplits);
    }

    @Override
    public BaseStatistics getStatistics(BaseStatistics cachedStatistics) throws IOException {
        return null;
    }

    @Override
    public void open(NodeInputSplit split) throws IOException {
        mlContext = prepareMLContext(split.getSplitNumber());
        preparePythonFiles();
        Runnable nodeServerRunnable = getNodeServerRunnable(mlContext);
        runRunnable(nodeServerRunnable, "NodeServer_" + mlContext.getIdentity());

        mlContext.getOutputQueue().markFinished();

        iniAndRunHookOpen();

        dataExchange = new DataExchange<>(mlContext);
    }

    @Override
    public boolean reachedEnd() throws IOException {
        return serverFuture.isDone() || dataExchange.getRecordReader().isReachEOF();
    }

    @Override
    public OUT nextRecord(OUT reuse) throws IOException {
        return dataExchange.read(true);
    }

    @Override
    public void close() throws IOException {
        synchronized (isClose) {
            if (!isClose.get()) {
                try {
                    if (serverFuture != null && !serverFuture.isCancelled()) {
                        serverFuture.get(closeTimeoutMs, TimeUnit.MILLISECONDS);
                    }
                } catch (ExecutionException e) {
                    LOG.error(mlContext.getIdentity() + " node server failed {}", e.getMessage());
                    throw new IOException(e);
                } catch (InterruptedException | TimeoutException e) {
                    LOG.error("Fail to join server {}", mlContext.getIdentity(), e);
                } finally {
                    if (serverFuture != null) {
                        serverFuture.cancel(true);
                    }
                    serverFuture = null;
                    if (mlContext != null) {
                        mlContext.close();
                        mlContext = null;
                    }
                }
                isClose.set(true);
            }
        }
        maybeRunHookClose();
    }

    private void runRunnable(Runnable runnable, String threadName) throws IOException {
        serverFuture = new FutureTask<>(runnable, null);
        try {
            Thread t = new Thread(serverFuture);
            t.setDaemon(true);
            t.setName(threadName);
            t.start();
        } catch (Exception e) {
            LOG.error("Fail to start node service.", e);
            throw new IOException(e.getMessage());
        }
        LOG.info("start: {}", threadName);
    }

    private void iniAndRunHookOpen() throws IOException {
        try {
            List<String> hookList = mlContext.getHookClassNames();
            hookManager = new FlinkOpHookManager(hookList);
            hookManager.open();
        } catch (Exception e) {
            e.printStackTrace();
            throw new IOException(e);
        }
    }

    private void maybeRunHookClose() throws IOException {
        if (null != hookManager) {
            try {
                hookManager.close();
            } catch (Exception e) {
                e.printStackTrace();
                throw new IOException(e);
            }
        }
    }

    protected abstract MLContext prepareMLContext(Integer nodeIndex) throws MLException;

    protected abstract Runnable getNodeServerRunnable(MLContext mlContext);

    @VisibleForTesting
    void preparePythonFiles() throws IOException {
        PythonFileUtil.preparePythonFilesForExec(getRuntimeContext(), mlContext);
    }

    @VisibleForTesting
    void waitServerFutureFinish() throws ExecutionException, InterruptedException {
        serverFuture.get();
    }

    @VisibleForTesting
    boolean isClosed() {
        return isClose.get();
    }
}
