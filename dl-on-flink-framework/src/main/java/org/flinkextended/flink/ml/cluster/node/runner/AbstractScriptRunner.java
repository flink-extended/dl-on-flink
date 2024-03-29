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
import org.flinkextended.flink.ml.util.SpscOffHeapQueue;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

/** Machine learning cluster node abstract script scriptRunner. */
public abstract class AbstractScriptRunner implements ScriptRunner {
    private static final Logger LOG = LoggerFactory.getLogger(AbstractScriptRunner.class);

    protected final MLContext mlContext;

    protected AbstractScriptRunner(MLContext mlContext) {
        this.mlContext = mlContext;
    }

    @Override
    public void close() throws IOException {
        SpscOffHeapQueue inputQueue = mlContext == null ? null : mlContext.getInputQueue();
        if (inputQueue != null) {
            LOG.info("{} mark input queue finished.", mlContext.getIdentity());
            inputQueue.markFinished();
        }
    }
}
