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

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.ExecutionStatus;
import org.flinkextended.flink.ml.cluster.node.runner.MLRunner;

/** Unit test for {@link MLRunner}. */
public class TestMLRunner implements MLRunner {

    private final MLContext context;
    private final NodeServer server;

    private boolean running;

    public TestMLRunner(MLContext context, NodeServer server) {
        this.context = context;
        this.server = server;
    }

    @Override
    public void initAMClient() throws Exception {}

    @Override
    public void getCurrentJobVersion() throws Exception {}

    @Override
    public void registerNode() throws Exception {}

    @Override
    public void startHeartBeat() throws Exception {}

    @Override
    public void waitClusterRunning() throws Exception {}

    @Override
    public void getClusterInfo() throws Exception {}

    @Override
    public void resetMLContext() throws Exception {}

    @Override
    public void runScript() throws Exception {}

    @Override
    public void notifyStop() throws Exception {
        running = false;
    }

    @Override
    public ExecutionStatus getResultStatus() {
        return null;
    }

    @Override
    public void run() {
        running = true;
    }

    public boolean isRunning() {
        return running;
    }
}
