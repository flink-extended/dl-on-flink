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

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.util.TestUtil;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.apache.curator.test.TestingServer;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.flinkextended.flink.ml.operator.client.TableTestUtil.execTableJobCustom;

/** Unit test for {@link PyTorchUtilLegacy}. */
public class PyTorchUtilLegacyTest {

    private static TestingServer testingServer;
    private static String rootPath =
            TestUtil.getProjectRootPath() + "/dl-on-flink-pytorch/src/test/python/";

    @Before
    public void setUp() throws Exception {
        testingServer = new TestingServer(2181, true);
    }

    @After
    public void tearDown() throws Exception {
        testingServer.stop();
    }

    @Test
    public void trainStream() throws Exception {
        PyTorchConfig pytorchConfig =
                new PyTorchConfig(3, null, rootPath + "greeter.py", "map_func", null);
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        PyTorchUtilLegacy.train(streamEnv, null, pytorchConfig, null);
        streamEnv.execute();
    }

    @Test
    public void trainTable() throws Exception {
        PyTorchConfig pytorchConfig =
                new PyTorchConfig(3, null, rootPath + "greeter.py", "map_func", null);
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        TableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        StatementSet statementSet = tableEnv.createStatementSet();
        PyTorchUtilLegacy.train(streamEnv, tableEnv, statementSet, null, pytorchConfig, null);
        execTableJobCustom(pytorchConfig.getMlConfig(), streamEnv, tableEnv, statementSet);
    }
}
