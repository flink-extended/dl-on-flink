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

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.operator.client.NodeUtils;

import org.apache.flink.annotation.Internal;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.iteration.DataStreamList;
import org.apache.flink.iteration.IterationBody;
import org.apache.flink.iteration.IterationBodyResult;
import org.apache.flink.iteration.IterationListener;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.types.Row;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * PyTorchNodeIterationBody is to build the subgraph that runs deep learning node in Flink iteration
 * and to consume the input data repeatedly.
 */
@Internal
public class PyTorchNodeIterationBody implements IterationBody {
    private final StreamExecutionEnvironment env;
    private final PyTorchClusterConfig pyTorchClusterConfig;
    private final Integer maxEpoch;
    private final Configuration flinkConfig;

    public PyTorchNodeIterationBody(
            StreamExecutionEnvironment env,
            PyTorchClusterConfig pyTorchClusterConfig,
            Integer maxEpoch,
            Configuration flinkConfig) {
        this.env = env;
        this.pyTorchClusterConfig = pyTorchClusterConfig;
        this.maxEpoch = maxEpoch;
        this.flinkConfig = flinkConfig;
    }

    @Override
    public IterationBodyResult process(DataStreamList variableStreams, DataStreamList dataStreams) {
        final DataStream<Row> input = dataStreams.get(0);
        final SingleOutputStreamOperator<Void> trainResStream =
                NodeUtils.scheduleNodes(
                        env,
                        input,
                        pyTorchClusterConfig,
                        TypeInformation.of(Void.class),
                        PyTorchClusterConfig.WORKER_NODE_TYPE,
                        flinkConfig);
        final DataStream<Integer> terminateStream =
                trainResStream
                        .getSideOutput(new OutputTag<Integer>("termination") {})
                        .flatMap(new TerminateOnEpoch(maxEpoch))
                        .name("TerminationDecider")
                        .setParallelism(1);
        final SingleOutputStreamOperator<Object> variable =
                variableStreams.get(0).map(i -> i).setParallelism(1);
        return new IterationBodyResult(
                DataStreamList.of(variable), DataStreamList.of(trainResStream), terminateStream);
    }

    /**
     * The FlatMapFunction that only emits values iff the upstream do not emit any value in the last
     * epoch or the current epoch reach the max epoch we should run.
     */
    public static class TerminateOnEpoch
            implements IterationListener<Integer>, FlatMapFunction<Integer, Integer> {

        private static final Logger LOG = LoggerFactory.getLogger(TerminateOnEpoch.class);

        private final Integer maxEpoch;
        private boolean earlyTerminated = true;

        public TerminateOnEpoch(Integer maxEpoch) {
            this.maxEpoch = maxEpoch;
        }

        @Override
        public void flatMap(Integer value, Collector<Integer> out) {
            earlyTerminated = false;
        }

        @Override
        public void onEpochWatermarkIncremented(
                int epochWatermark, Context context, Collector<Integer> collector) {
            if (earlyTerminated) {
                LOG.info("Early Terminated at epoch {}", epochWatermark);
                return;
            }
            if (epochWatermark >= maxEpoch - 1) {
                LOG.info("Terminate at epoch {}", epochWatermark);
                return;
            }

            collector.collect(epochWatermark);
            earlyTerminated = true;
        }

        @Override
        public void onIterationTerminated(Context context, Collector<Integer> collector) {}
    }
}
