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

package org.flinkextended.flink.ml.operator.ops.source;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.role.BaseRole;
import org.flinkextended.flink.ml.operator.ops.inputformat.AMInputFormat;
import org.flinkextended.flink.ml.operator.ops.inputformat.MLInputFormat;
import org.flinkextended.flink.ml.operator.ops.inputformat.NodeInputFormat;
import org.flinkextended.flink.ml.operator.ops.inputformat.NodeInputSplit;

import org.apache.flink.api.common.io.InputFormat;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.source.InputFormatSourceFunction;

/**
 * flink source operator wrapper machine learning cluster node.
 *
 * @param <OUT> machine learning cluster node output object class.
 */
public class NodeSource<OUT> extends InputFormatSourceFunction<OUT>
        implements ResultTypeQueryable<OUT> {

    private final TypeInformation<OUT> outTypeInformation;

    public NodeSource(InputFormat<OUT, NodeInputSplit> format, TypeInformation<OUT> typeInfo) {
        super(format, typeInfo);
        outTypeInformation = typeInfo;
    }

    /**
     * create machine learning cluster node or application master plan as flink source operator.
     *
     * @param mode machine learning execution mode: train inference other.
     * @param role machine learning cluster role.
     * @param config machine learning cluster configuration.
     * @param outTI machine learning node output flink type information.
     * @param <OUT> machine learning node output class.
     * @return flink source wrapper machine learning cluster node.
     */
    public static <OUT> NodeSource<OUT> createSource(
            ExecutionMode mode, BaseRole role, MLConfig config, TypeInformation<OUT> outTI) {
        MLInputFormat<OUT> tfInputFormat = new MLInputFormat<>(mode, role, config, outTI);
        return new NodeSource<>(tfInputFormat, outTI);
    }

    /**
     * Create a deep learning cluster node with the given node type and the given {@link
     * ClusterConfig} as Flink source.
     *
     * @param nodeType The node type of the node.
     * @param config The ClusterConfig of the node.
     * @param outTI The output type of the node.
     * @param flinkConfig The flink configuration.
     * @return Flink source that runs the node.
     */
    public static <OUT> NodeSource<OUT> createNodeSource(
            String nodeType,
            ClusterConfig config,
            TypeInformation<OUT> outTI,
            Configuration flinkConfig) {
        final NodeInputFormat<OUT> inputFormat =
                new NodeInputFormat<>(nodeType, config, flinkConfig);
        return new NodeSource<>(inputFormat, outTI);
    }

    /**
     * Create a deep learning cluster Application Master node as Flink source with the {@link
     * ClusterConfig}.
     *
     * @param config The ClusterConfig of the node.
     * @return Flink Source that runs the Application Master.
     */
    public static NodeSource<Void> createAMNodeSource(ClusterConfig config) {
        final AMInputFormat amInputFormat = new AMInputFormat(config);
        return new NodeSource<>(amInputFormat, TypeInformation.of(Void.class));
    }

    @Override
    public TypeInformation<OUT> getProducedType() {
        return outTypeInformation;
    }
}
