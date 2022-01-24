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

package org.flinkextended.flink.ml.operator.util;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.io.IOException;

import static org.flinkextended.flink.ml.util.DummyContext.createDummyMLConfig;
import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.verify;

public class PythonFileUtilTest {

    @Test
    public void testRegisterPythonLibFilesWithoutScheme() throws IOException {
        final StreamExecutionEnvironment env = Mockito.mock(StreamExecutionEnvironment.class);
        final ArgumentCaptor<String> nameCaptor = ArgumentCaptor.forClass(String.class);
        final ArgumentCaptor<String> pathCaptor = ArgumentCaptor.forClass(String.class);
        final MLConfig mlConfig = createDummyMLConfig();
        mlConfig.setPythonFiles(new String[]{"/tmp/test.py"});
        PythonFileUtil.registerPythonFiles(env, mlConfig);

        verify(env).registerCachedFile(pathCaptor.capture(), nameCaptor.capture());
        assertEquals("/tmp/test.py", pathCaptor.getValue());
        assertEquals("test.py", nameCaptor.getValue());
    }

}