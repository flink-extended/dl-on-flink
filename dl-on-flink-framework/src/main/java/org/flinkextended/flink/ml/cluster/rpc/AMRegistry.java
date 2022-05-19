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

package org.flinkextended.flink.ml.cluster.rpc;

import org.flinkextended.flink.ml.cluster.master.meta.AMMeta;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.FlinkKillException;
import org.flinkextended.flink.ml.cluster.storage.Storage;
import org.flinkextended.flink.ml.cluster.storage.StorageFactory;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.TimeoutException;

/** The class to discover where is the AM node and how to create an AMClient. */
public class AMRegistry {
    private static final Logger LOG = LoggerFactory.getLogger(AMRegistry.class);
    private static final Duration WAIT_INTERVAL = Duration.ofSeconds(5);

    /**
     * Discover where AM is and return an AMClient to communicate with this AM.
     *
     * @return the AMClient.
     */
    public static AMClient getAMClient(MLContext mlContext) throws IOException {
        long timeout =
                Long.valueOf(
                        mlContext
                                .getProperties()
                                .getOrDefault(
                                        MLConstants.AM_REGISTRY_TIMEOUT,
                                        MLConstants.AM_REGISTRY_TIMEOUT_DEFAULT));
        return getAMClient(mlContext, timeout);
    }

    public static AMClient getAMClient(MLContext mlContext, long timeout) throws IOException {
        return getAMClient(mlContext.getProperties(), timeout);
    }

    public static AMClient getAMClient(Map<String, String> properties, long timeout)
            throws IOException {
        Storage storage = null;
        AMClient client = null;
        try {
            storage = StorageFactory.getStorageInstance(properties);
            long startTime = System.currentTimeMillis();
            while (true) {
                long duration = System.currentTimeMillis() - startTime;
                if (duration > timeout) {
                    if (client != null) {
                        client.close();
                    }
                    throw new MLException(
                            "Fail to get AM connection.",
                            new TimeoutException(
                                    String.format(
                                            "AM not ready after %d seconds time out %d",
                                            duration / 1000, timeout / 1000)));
                }
                byte[] bytes = storage.getValue(AMMeta.AM_ADDRESS);
                if (bytes == null) {
                    Thread.sleep(WAIT_INTERVAL.toMillis());
                } else {
                    String ipPortStr = new String(bytes);
                    LOG.info("AM address is: " + ipPortStr);
                    String[] ipPort = new String(bytes).split(":");
                    if (2 != ipPort.length) {
                        LOG.error("AM ip port not validate:" + ipPortStr);
                        if (client != null) {
                            client.close();
                        }
                        throw new MLException("AM ip port not validate:" + ipPortStr);
                    }
                    String host = ipPort[0];
                    int port = Integer.valueOf(ipPort[1]);
                    if (client == null
                            || !client.getHost().equals(host)
                            || client.getPort() != port) {
                        if (client != null) {
                            client.close();
                        }
                        client = new AMClient(host, port);
                    }
                    // make sure the client is ready, in case the am address is outdated
                    if (client.waitForReady(WAIT_INTERVAL)) {
                        return client;
                    }
                }
            }
        } catch (InterruptedException e) {
            if (client != null) {
                client.close();
            }
            throw new FlinkKillException("Interrupted getting AM client", e);
        } finally {
            if (storage != null) {
                storage.close();
            }
        }
    }
}
