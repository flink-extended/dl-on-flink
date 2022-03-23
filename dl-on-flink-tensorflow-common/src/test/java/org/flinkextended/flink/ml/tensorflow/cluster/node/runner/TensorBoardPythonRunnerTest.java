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

package org.flinkextended.flink.ml.tensorflow.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;

import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

import static org.junit.Assert.assertEquals;

/** Unit test for {@link TensorBoardPythonRunner}. */
public class TensorBoardPythonRunnerTest {

    @Test
    public void testRunScript() throws IOException {
        final MLContext mlContext = DummyContext.createDummyMLContext();
        mlContext.setPythonDir(Paths.get("/tmp"));
        mlContext.setPythonFiles(new String[] {"tensorboard.py"});
        final TensorBoardPythonRunner tensorboardRunner =
                Mockito.spy(new TensorBoardPythonRunner(mlContext));
        ArgumentCaptor<ProcessBuilder> captor = ArgumentCaptor.forClass(ProcessBuilder.class);
        Mockito.doNothing().when(tensorboardRunner).runProcess(captor.capture());
        tensorboardRunner.runScript();
        final List<String> command = captor.getValue().command();
        assertEquals(5, command.size());
        assertEquals("python", command.get(0));
        assertEquals("/tmp/tensorboard.py", command.get(1));
    }
}
