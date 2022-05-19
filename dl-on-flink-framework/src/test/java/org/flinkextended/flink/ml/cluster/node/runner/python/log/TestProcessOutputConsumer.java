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

package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.cluster.node.MLContext;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/** Dummy {@link AbstractProcessOutputConsumer} for unit test. */
public class TestProcessOutputConsumer extends AbstractProcessOutputConsumer {
    private final List<String> stdOutLog = new ArrayList<>();
    private final List<String> stdErrLog = new ArrayList<>();

    public TestProcessOutputConsumer(MLContext mlContext) {
        super(mlContext);
    }

    @Override
    Consumer<String> getStdOutConsumer() {
        return stdOutLog::add;
    }

    @Override
    Consumer<String> getStdErrConsumer() {
        return stdErrLog::add;
    }

    public List<String> getStdOutLog() {
        return stdOutLog;
    }

    public List<String> getStdErrLog() {
        return stdErrLog;
    }
}
