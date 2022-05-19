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

package org.flinkextended.flink.ml.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.AMClient;
import org.flinkextended.flink.ml.cluster.rpc.AMRegistry;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.cluster.rpc.RpcCode;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.proto.SimpleResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

/** Created by node, handle node send heart beat message to am Server(AppMasterServer). */
public class NodeHeartBeatRunner implements Runnable {
    private static final Logger LOG = LoggerFactory.getLogger(NodeHeartBeatRunner.class);

    private static final long interval = 5000;
    private volatile boolean stop = false;
    private Exception lastException = null;
    private AMClient amClient;
    private final MLContext mlContext;
    private final NodeServer server;
    private final NodeSpec nodeSpec;
    private final long version;

    public NodeHeartBeatRunner(
            MLContext mlContext, NodeServer server, NodeSpec nodeSpec, long version) {
        super();
        this.mlContext = mlContext;
        this.server = server;
        this.nodeSpec = nodeSpec;
        this.version = version;
        this.amClient = null;
    }

    // stop heartbeat thread
    public void setStopFlag(boolean stopFlag) {
        this.stop = stopFlag;
    }

    @Override
    public void run() {
        try {
            while (!stop) {
                try {
                    Thread.sleep(interval);
                    if (null == amClient) {
                        amClient = AMRegistry.getAMClient(mlContext, 1000);
                    }
                    SimpleResponse response = amClient.heartbeat(version, nodeSpec);
                    if (response.getCode() == RpcCode.VERSION_ERROR.ordinal()) {
                        LOG.warn(
                                "{} heartbeat wrong version {}, terminating heartbeat thread and restart tf node",
                                mlContext.getIdentity(),
                                version);
                        server.setAmCommand(NodeServer.AMCommand.RESTART);
                        break;
                    }
                    if (response.getCode() != RpcCode.OK.ordinal()) {
                        LOG.warn(
                                "{} heartbeat response code {}",
                                mlContext.getIdentity(),
                                response.getCode());
                    }
                    lastException = null;
                } catch (InterruptedException e) {
                    LOG.info("{} heartbeat thread interrupted", mlContext.getIdentity());
                    return;
                } catch (Exception e) {
                    if (lastException != null
                            && lastException.getMessage().equals(e.getMessage())) {
                        LOG.warn(
                                "{} heartbeat failed with same reason: {}, stacktrace suppressed",
                                mlContext.getIdentity(),
                                lastException.getMessage());
                    } else {
                        LOG.warn(
                                "{} failed to send heartbeat to AM {}",
                                mlContext.getIdentity(),
                                e.getMessage());
                        lastException = e;
                    }
                    try {
                        if (amClient != null) {
                            LOG.info("{} closing old AM connection", mlContext.getIdentity());
                            amClient.close();
                            amClient = null;
                        }
                        amClient = AMRegistry.getAMClient(mlContext, 1000);
                        LOG.info("{} reconnect AM connection", mlContext.getIdentity());
                    } catch (IOException e1) {
                        LOG.warn(
                                "{} failed to update am address error {}",
                                mlContext.getIdentity(),
                                e1.getMessage());
                        lastException = e1;
                    }
                }
            }
        } finally {
            if (null != amClient) {
                amClient.close();
                amClient = null;
            }
        }
    }
}
