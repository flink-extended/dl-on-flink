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

package org.flinkextended.flink.ml.cluster.node.runner.python;

import org.flinkextended.flink.ml.TestWithNodeService;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.python.log.Slf4JProcessOutputConsumer;
import org.flinkextended.flink.ml.coding.impl.ByteArrayCodingImpl;
import org.flinkextended.flink.ml.data.DataExchange;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.TestUtil;

import com.alibaba.fastjson.JSONObject;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Paths;

/** Unit test for {@link ProcessPythonRunner}. */
public class ProcessPythonRunnerTest extends TestWithNodeService {
    private static final Logger Logger = LoggerFactory.getLogger(ProcessPythonRunnerTest.class);

    public MLContext createMLContext(String scriptName) throws Exception {
        String rootPath = TestUtil.getProjectRootPath() + "/dl-on-flink-framework/src/test/python";

        MLContext context = DummyContext.createDummyMLContext();
        context.setPythonDir(Paths.get(rootPath));
        context.setPythonFiles(new String[] {scriptName});
        context.setFuncName("map_func");
        configureContext(context);
        return context;
    }

    @Test
    public void greeterPythonTest() throws Exception {
        String script = "greeter.py";
        MLContext mlContext = createMLContext(script);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
    }

    @Test
    public void greeterPythonTestToSlf4j() throws Exception {
        String script = "greeter.py";
        MLContext mlContext = createMLContext(script);
        mlContext
                .getProperties()
                .put(
                        MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS,
                        Slf4JProcessOutputConsumer.class.getCanonicalName());
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
    }

    @Test
    public void pythonReadFromJavaTest() throws Exception {
        String script = "read_from_java.py";
        MLContext mlContext = createMLContext(script);
        DataExchange<JSONObject, JSONObject> dataExchange = new DataExchange<>(mlContext);
        JSONObject object = new JSONObject();
        object.put("a", "a");
        dataExchange.write(object);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
    }

    @Test
    public void pythonWriteToJavaTest() throws Exception {
        String script = "write_to_java.py";
        MLContext mlContext = createMLContext(script);
        DataExchange<JSONObject, JSONObject> dataExchange = new DataExchange<>(mlContext);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
        JSONObject object = dataExchange.read(true);
        System.out.println("res:" + object.toJSONString());
    }

    @Test
    public void pythonReadBytesFromJavaTest() throws Exception {
        String script = "read_bytes_from_java.py";
        MLContext mlContext = createMLContext(script);
        mlContext
                .getProperties()
                .put(MLConstants.DECODING_CLASS, ByteArrayCodingImpl.class.getCanonicalName());
        mlContext
                .getProperties()
                .put(MLConstants.ENCODING_CLASS, ByteArrayCodingImpl.class.getCanonicalName());
        DataExchange<byte[], byte[]> dataExchange = new DataExchange<>(mlContext);
        byte[] object = "aaaaa".getBytes();
        dataExchange.write(object);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
    }

    @Test
    public void pythonWriteBytesToJavaTest() throws Exception {
        String script = "write_bytes_to_java.py";
        MLContext mlContext = createMLContext(script);
        mlContext
                .getProperties()
                .put(MLConstants.DECODING_CLASS, ByteArrayCodingImpl.class.getCanonicalName());
        mlContext
                .getProperties()
                .put(MLConstants.ENCODING_CLASS, ByteArrayCodingImpl.class.getCanonicalName());
        DataExchange<byte[], byte[]> dataExchange = new DataExchange<>(mlContext);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
        byte[] object = dataExchange.read(true);
        Logger.info("res:" + new String(object));
    }

    @Test
    public void pythonReadJsonFromJavaTest() throws Exception {
        String script = "read_json_from_java.py";
        MLContext mlContext = createMLContext(script);
        DataExchange<JSONObject, JSONObject> dataExchange = new DataExchange<>(mlContext);
        JSONObject object = new JSONObject();
        object.put("json_read", "json_read");
        dataExchange.write(object);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
    }

    @Test
    public void pythonWriteJsonToJavaTest() throws Exception {
        String script = "write_json_to_java.py";
        MLContext mlContext = createMLContext(script);
        DataExchange<JSONObject, JSONObject> dataExchange = new DataExchange<>(mlContext);
        ProcessPythonRunner runner = new ProcessPythonRunner(mlContext);
        runner.runScript();
        JSONObject object = dataExchange.read(true);
        Logger.info("res:" + object.toJSONString());
    }
}
