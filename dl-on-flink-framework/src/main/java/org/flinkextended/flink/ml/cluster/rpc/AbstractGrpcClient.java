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

package org.flinkextended.flink.ml.cluster.rpc;

import io.grpc.ConnectivityState;
import io.grpc.ManagedChannel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Closeable;
import java.time.Duration;
import java.util.concurrent.TimeUnit;

/** AbstractGrpcClient. */
public abstract class AbstractGrpcClient implements Closeable {
    private static final Logger LOG = LoggerFactory.getLogger(AbstractGrpcClient.class);

    protected final String host;
    protected final int port;
    protected final ManagedChannel grpcChannel;

    public AbstractGrpcClient(String host, int port, ManagedChannel grpcChannel) {
        this.host = host;
        this.port = port;
        this.grpcChannel = grpcChannel;
    }

    /**
     * The name of the server that the client is connecting to. The name is used mainly for logging
     * purpose.
     *
     * @return he name of the server that the client is connecting to.
     */
    abstract String serverName();

    @Override
    public void close() {
        LOG.info("close {} client", serverName());
        if (grpcChannel != null) {
            grpcChannel.shutdown();
            try {
                boolean res = grpcChannel.awaitTermination(2, TimeUnit.MINUTES);
                LOG.info("{} client channel termination: {}", serverName(), res);
            } catch (InterruptedException e) {
                LOG.error("{} client termination interrupted.", serverName(), e);
            }
        }
    }

    /**
     * Wait until the grpc channel is ready.
     *
     * @param duration time out
     * @return the boolean indicating the grpc channel is ready or not when return.
     * @throws InterruptedException if the current thread is interrupted
     */
    public boolean waitForReady(Duration duration) throws InterruptedException {
        final long deadline = System.currentTimeMillis() + duration.toMillis();
        while (grpcChannel.getState(true) != ConnectivityState.READY) {
            if (System.currentTimeMillis() > deadline) {
                return false;
            }
            //noinspection BusyWait
            Thread.sleep(1000);
        }
        return true;
    }

    public String getHost() {
        return host;
    }

    public int getPort() {
        return port;
    }
}
