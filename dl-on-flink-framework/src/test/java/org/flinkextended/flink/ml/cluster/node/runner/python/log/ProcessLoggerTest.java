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

import org.flinkextended.flink.ml.util.DummyContext;

import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;

/** Unit test for {@link ProcessLogger}. */
public class ProcessLoggerTest {
    @Test
    public void testProcessLoggerStdOut() throws IOException, InterruptedException {
        final ProcessBuilder builder = new ProcessBuilder("echo", "hello");
        final Process process = builder.start();

        final TestProcessOutputConsumer consumer =
                new TestProcessOutputConsumer(DummyContext.createDummyMLContext());
        final ProcessLogger logger = new ProcessLogger("test", process, consumer);
        logger.start_logging();
        process.waitFor();
        while (consumer.getStdOutLog().size() == 0) {
            Thread.sleep(100);
        }
        assertEquals("hello", consumer.getStdOutLog().get(0));
    }

    @Test
    public void testProcessLoggerStdErr() throws IOException, InterruptedException {
        final ProcessBuilder builder =
                new ProcessBuilder("python", "-c", "import sys;sys.stderr.write('error')");
        final Process process = builder.start();

        final TestProcessOutputConsumer consumer =
                new TestProcessOutputConsumer(DummyContext.createDummyMLContext());
        final ProcessLogger logger = new ProcessLogger("test", process, consumer);
        logger.start_logging();
        process.waitFor();
        while (consumer.getStdErrLog().size() == 0) {
            Thread.sleep(100);
        }
        assertEquals("error", consumer.getStdErrLog().get(0));
    }
}
