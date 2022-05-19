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

import java.io.IOException;

/** Dummy {@link AbstractScriptRunner} for unit test. */
public class TestScriptRunner extends AbstractScriptRunner {
    private boolean ran = false;

    public TestScriptRunner(MLContext mlContext) {
        super(mlContext);
    }

    @Override
    public void runScript() throws IOException {
        ran = true;
        // do nothing
    }

    @Override
    public void notifyKillSignal() {
        // do nothing
    }

    public boolean isRan() {
        return ran;
    }
}
