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

package org.flinkextended.flink.ml.tensorflow.client;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.operator.ops.NodeOperator;
import org.flinkextended.flink.ml.operator.ops.inputformat.AMInputFormat;
import org.flinkextended.flink.ml.operator.ops.inputformat.NodeInputFormat;
import org.flinkextended.flink.ml.operator.ops.source.NodeSource;

import org.apache.flink.api.common.io.InputFormat;
import org.apache.flink.iteration.operator.WrapperOperatorFactory;
import org.apache.flink.streaming.api.graph.StreamNode;
import org.apache.flink.streaming.api.operators.SimpleOperatorFactory;
import org.apache.flink.streaming.api.operators.StreamSource;

import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;

class StreamNodeMatchers {

    public static class StreamNodeMatcher extends BaseMatcher<StreamNode> {
        protected final String operatorName;
        protected final int parallelism;

        public StreamNodeMatcher(String operatorName, int parallelism) {

            this.operatorName = operatorName;
            this.parallelism = parallelism;
        }

        @Override
        public boolean matches(Object o) {
            final StreamNode streamNode = getStreamNode(o);
            if (streamNode == null) {
                return false;
            }

            return streamNode.getOperatorName().contains(operatorName)
                    && streamNode.getParallelism() == parallelism;
        }

        protected StreamNode getStreamNode(Object o) {
            if (!(o instanceof StreamNode)) {
                return null;
            }
            return (StreamNode) o;
        }

        @Override
        public void describeTo(Description description) {
            description.appendText(
                    String.format(
                            "StreamNode{name contains %s, parallelism = %d}",
                            operatorName, parallelism));
        }
    }

    public static class AMNodeMatcher extends StreamNodeMatcher {

        public AMNodeMatcher(int parallelism) {
            super(ClusterConfig.AM_NODE_TYPE, parallelism);
        }

        @Override
        public boolean matches(Object o) {
            if (!super.matches(o)) {
                return false;
            }
            try {
                final StreamNode streamNode = getStreamNode(o);
                final StreamSource<?, ?> operator = (StreamSource<?, ?>) streamNode.getOperator();
                final NodeSource<?> nodeSource = (NodeSource<?>) operator.getUserFunction();
                final InputFormat<?, ?> format = nodeSource.getFormat();
                return format instanceof AMInputFormat;
            } catch (ClassCastException e) {
                return false;
            }
        }
    }

    public static class SourceNodeMatcher extends StreamNodeMatcher {

        public SourceNodeMatcher(String nodeType, int parallelism) {
            super(nodeType, parallelism);
        }

        @Override
        public boolean matches(Object o) {
            if (!super.matches(o)) {
                return false;
            }
            try {
                final StreamNode streamNode = getStreamNode(o);
                final StreamSource<?, ?> operator = (StreamSource<?, ?>) streamNode.getOperator();
                final NodeSource<?> nodeSource = (NodeSource<?>) operator.getUserFunction();
                final InputFormat<?, ?> format = nodeSource.getFormat();
                return format instanceof NodeInputFormat
                        && ((NodeInputFormat<?>) format).getNodeType().equals(operatorName);
            } catch (ClassCastException e) {
                return false;
            }
        }
    }

    public static class NodeOperatorMatcher extends StreamNodeMatcher {

        public NodeOperatorMatcher(String nodeType, int parallelism) {
            super(nodeType, parallelism);
        }

        @Override
        public boolean matches(Object o) {
            if (!super.matches(o)) {
                return false;
            }
            try {
                final StreamNode streamNode = getStreamNode(o);
                final NodeOperator<?> operator = (NodeOperator<?>) streamNode.getOperator();
                return operator.getNodeType().equals(operatorName);
            } catch (ClassCastException e) {
                return false;
            }
        }
    }

    public static class IterativeNodeOperatorMatcher extends StreamNodeMatcher {

        public IterativeNodeOperatorMatcher(String nodeType, int parallelism) {
            super(nodeType, parallelism);
        }

        @Override
        public boolean matches(Object o) {
            if (!super.matches(o)) {
                return false;
            }
            try {
                final StreamNode streamNode = getStreamNode(o);
                final NodeOperator<?> operator =
                        (NodeOperator<?>)
                                ((SimpleOperatorFactory<?>)
                                                ((WrapperOperatorFactory<?>)
                                                                streamNode.getOperatorFactory())
                                                        .getOperatorFactory())
                                        .getOperator();
                return operator.getNodeType().equals(operatorName);
            } catch (ClassCastException e) {
                return false;
            }
        }
    }
}
