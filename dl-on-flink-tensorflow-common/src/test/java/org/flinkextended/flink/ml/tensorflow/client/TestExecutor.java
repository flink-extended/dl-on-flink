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

package org.flinkextended.flink.ml.tensorflow.client;

import org.apache.flink.api.common.JobExecutionResult;
import org.apache.flink.api.dag.Pipeline;
import org.apache.flink.api.dag.Transformation;
import org.apache.flink.configuration.ReadableConfig;
import org.apache.flink.core.execution.JobClient;
import org.apache.flink.table.delegation.Executor;

import javax.annotation.Nullable;

import java.util.List;

class TestExecutor implements Executor {

    private final Executor executor;
    private Pipeline pipeline;

    public TestExecutor(Executor executor) {
        this.executor = executor;
    }

    @Override
    public ReadableConfig getConfiguration() {
        return executor.getConfiguration();
    }

    @Override
    public Pipeline createPipeline(
            List<Transformation<?>> list, ReadableConfig readableConfig, @Nullable String s) {
        return executor.createPipeline(list, readableConfig, s);
    }

    @Override
    public JobExecutionResult execute(Pipeline pipeline) throws Exception {
        this.pipeline = pipeline;
        return null;
    }

    @Override
    public JobClient executeAsync(Pipeline pipeline) {
        this.pipeline = pipeline;
        return null;
    }

    public Pipeline getPipeline() {
        return pipeline;
    }
}
