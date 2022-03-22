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
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLConstants;

import org.junit.Test;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

/** Unit test for {@link ProcessOutputConsumerFactory}. */
public class ProcessOutputConsumerFactoryTest {
    @Test
    public void testGetDefaultLoggerConsumer() {
        final AbstractProcessOutputConsumer loggerConsumer =
                ProcessOutputConsumerFactory.createMLRunner(DummyContext.createDummyMLContext());
        assertTrue(loggerConsumer instanceof StdOutErrorProcessOutputConsumer);
    }

    @Test
    public void testGetLoggerConsumer() {
        final MLContext mlContext = DummyContext.createDummyMLContext();
        mlContext
                .getProperties()
                .put(
                        MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS,
                        TestProcessOutputConsumer.class.getCanonicalName());
        final AbstractProcessOutputConsumer loggerConsumer =
                ProcessOutputConsumerFactory.createMLRunner(mlContext);
        assertThat(loggerConsumer, instanceOf(TestProcessOutputConsumer.class));
    }
}
