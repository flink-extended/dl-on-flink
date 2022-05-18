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
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.ReflectUtil;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Factory for {@link AbstractProcessOutputConsumer}. */
public class ProcessOutputConsumerFactory {
    private static final Logger LOG = LoggerFactory.getLogger(ProcessOutputConsumerFactory.class);

    public static AbstractProcessOutputConsumer createMLRunner(MLContext mlContext) {
        String className =
                mlContext.getProperties().get(MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS);

        // default logger consumer
        if (className == null) {
            LOG.info(
                    "property {} is not set. Python process log will send to stdout/stderr",
                    MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS);
            return getDefaultLoggerConsumer(mlContext);
        }

        try {
            Class[] classes = new Class[1];
            classes[0] = MLContext.class;
            Object[] objects = new Object[1];
            objects[0] = mlContext;
            return ReflectUtil.createInstance(className, classes, objects);
        } catch (Exception e) {
            LOG.warn(
                    "Fail to instantiate ProcessLoggerConsumer {}. Process log will send to stdout/stderr",
                    className,
                    e);
        }

        return getDefaultLoggerConsumer(mlContext);
    }

    private static AbstractProcessOutputConsumer getDefaultLoggerConsumer(MLContext context) {
        return new StdOutErrorProcessOutputConsumer(context);
    }
}
