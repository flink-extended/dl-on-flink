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

package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.ShellExec;

import java.util.function.Consumer;

/**
 * {@link StdOutErrorProcessOutputConsumer} consumes stdout and stderr of the deep learning process
 * and print to the stdout and stderr of the Java process.
 */
public class StdOutErrorProcessOutputConsumer extends AbstractProcessOutputConsumer {
    StdOutErrorProcessOutputConsumer(MLContext mlContext) {
        super(mlContext);
    }

    @Override
    public Consumer<String> getStdOutConsumer() {
        return new ShellExec.StdOutConsumer();
    }

    @Override
    public Consumer<String> getStdErrConsumer() {
        return new ShellExec.StdErrorConsumer();
    }
}
