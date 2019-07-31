package com.alibaba.flink.ml.tensorflow.coding;

import com.alibaba.flink.ml.tensorflow.client.TFConfig;
import com.alibaba.flink.ml.tensorflow.client.TFUtils;
import com.alibaba.flink.ml.util.MLConstants;
import com.alibaba.flink.ml.util.TestUtil;
import org.apache.curator.test.TestingServer;
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.api.java.StreamTableEnvironment;
import org.apache.flink.types.Row;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ExampleInputOutputTest {
    private static final String ZookeeperConn = "127.0.0.1:2181";
    private static final String[] Scripts = {TestUtil.getProjectRootPath() + "/flink-ml-tensorflow/src/test/python/example_coding.py"};
    private static final int WorkerNum = 1;
    private static final int PsNum = 0;

    private TestingServer server;

    @Before
    public void start() throws Exception {
        server = new TestingServer(2181, true);
    }

    @After
    public void stop() throws Exception {
        if (server != null) {
            server.stop();
        }
    }

    @Test
    public void testExampleCoding() throws Exception {
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.createLocalEnvironment(1);
        streamEnv.setRestartStrategy(restartStrategy());
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        Table input = tableEnv.fromDataStream(streamEnv.fromCollection(createDummyData()).setParallelism(1), "input");
        TFConfig config = createTFConfig("test_example_coding");
        TableSchema inputSchema = new TableSchema(new String[]{"input"}, new TypeInformation[]{BasicTypeInfo.STRING_TYPE_INFO});
        TableSchema outputSchema = new TableSchema(new String[]{"output"}, new TypeInformation[]{BasicTypeInfo.STRING_TYPE_INFO});
        CodingUtils.configureExampleCoding(config, inputSchema, outputSchema, ExampleCodingConfig.ObjectType.ROW, Row.class);
        Table output = TFUtils.inference(streamEnv, tableEnv, input, config, outputSchema);
        tableEnv.toAppendStream(output, Row.class).print().setParallelism(1);
        streamEnv.execute();
    }

    @Test
    public void testExampleCodingWithoutEncode() throws Exception {
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.createLocalEnvironment(1);
        streamEnv.setRestartStrategy(restartStrategy());
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        TFConfig config = createTFConfig("test_example_coding_without_encode");
        TableSchema inputSchema = null;
        TableSchema outputSchema = new TableSchema(new String[]{"output"}, new TypeInformation[]{BasicTypeInfo.STRING_TYPE_INFO});
        CodingUtils.configureExampleCoding(config, inputSchema, outputSchema, ExampleCodingConfig.ObjectType.ROW, Row.class);
        Table output = TFUtils.inference(streamEnv, tableEnv, null, config, outputSchema);
        tableEnv.toAppendStream(output, Row.class).print().setParallelism(1);
        streamEnv.execute();
    }

    @Test
    public void testExampleCodingWithoutDecode() throws Exception {
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.createLocalEnvironment(1);
        streamEnv.setRestartStrategy(restartStrategy());
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        Table input = tableEnv.fromDataStream(streamEnv.fromCollection(createDummyData()).setParallelism(1), "input");
        TFConfig config = createTFConfig("test_example_coding_without_decode");
        TableSchema inputSchema = new TableSchema(new String[]{"input"}, new TypeInformation[]{BasicTypeInfo.STRING_TYPE_INFO});
        TableSchema outputSchema = null;
        CodingUtils.configureExampleCoding(config, inputSchema, outputSchema, ExampleCodingConfig.ObjectType.ROW, Row.class);
        Table output = TFUtils.inference(streamEnv, tableEnv, input, config, outputSchema);
        streamEnv.execute();
    }

    @Test
    public void testExampleCodingWithNothing() throws Exception {
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.createLocalEnvironment(1);
        streamEnv.setRestartStrategy(restartStrategy());
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        TFConfig config = createTFConfig("test_example_coding_with_nothing");
        TableSchema outputSchema = null;
        Table output = TFUtils.inference(streamEnv, tableEnv, null, config, outputSchema);
        streamEnv.execute();
    }

    private List<Row> createDummyData() {
        List<Row> rows = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            Row row = new Row(1);
            row.setField(0, String.format("data-%d", i));
            rows.add(row);
        }
        return rows;
    }

    private TFConfig createTFConfig(String mapFunc) {
        Map<String, String> prop = new HashMap<>();
        prop.put(MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_ZOOKEEPER);
        prop.put(MLConstants.CONFIG_ZOOKEEPER_CONNECT_STR, ZookeeperConn);
        return new TFConfig(WorkerNum, PsNum, prop, Scripts, mapFunc, null);
    }

    private RestartStrategies.RestartStrategyConfiguration restartStrategy() {
        return RestartStrategies.noRestart();
    }
}
