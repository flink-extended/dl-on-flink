package com.alibaba.flink.ml.lib.tensorflow;

import com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowOptions;
import com.alibaba.flink.ml.lib.tensorflow.util.ShellExec;
import com.alibaba.flink.ml.operator.util.TypeUtil;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.util.Properties;

public class TFInferenceUDTFTest {

    @Before
    public void setUp() throws Exception {
        String pythonScriptPath = this.getClass().getClassLoader().getResource("").getPath()
                + "../../src/test/python/";
        String pythonScript = pythonScriptPath + "add_saved_model.py";
        String modelDir = this.getClass().getClassLoader().getResource("").getPath() + "export";
        File f = new File(modelDir);
        if (!f.exists()) {
            Assert.assertTrue(ShellExec.run("python " + pythonScript));
        }
        String pythonScript2 = pythonScriptPath + "build_model.py";
        String modelDir2 = this.getClass().getClassLoader().getResource("").getPath() + "export2";
        File f2 = new File(modelDir2);
        if (!f2.exists()) {
            Assert.assertTrue(ShellExec.run("python " + pythonScript2));
        }
    }

    @After
    public void tearDown() throws Exception {
    }

    @Test
    public void eval() throws Exception {
        String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath() + "export";
        String inputNames = "a,b";
        String inputTypes = "DT_FLOAT, DT_FLOAT";
        String inputRanks = "0, 0";
        String outputNames = "d";
        String outputTypes = "DT_FLOAT";
        String outputRanks = "0";
        TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
                outputNames, outputTypes, outputRanks,
                new Properties(), 5);
        TypeInformation[] types = new TypeInformation[1];
        types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
        RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames.split(","));

        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        streamEnv.setParallelism(1);
        tableEnv.createTemporaryTable("source", TableDescriptor
                .forConnector("TableDebugRow")
                .schema(Schema.newBuilder()
                        .column("a", DataTypes.FLOAT())
                        .column("b", DataTypes.FLOAT())
                        .build())
                .build());

        tableEnv.registerFunction("inference", predictUDTF);

        tableEnv.createTemporaryTable("sink", TableDescriptor
                .forConnector("print")
                .schema(TypeUtil.rowTypeInfoToSchema(typeInfo))
                .build());

        tableEnv.executeSql(
                "INSERT INTO sink SELECT d FROM source, LATERAL TABLE(inference(a, b)) as T(d)")
                .getJobClient().get()
                .getJobExecutionResult().get();
    }

    @Test
    public void eval2() throws Exception {
        String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath() + "export";
        String inputNames = "a,b";
        String inputTypes = "DT_FLOAT, DT_FLOAT";
        String inputRanks = "0, 0";
        String outputNames = "d,a";
        String outputTypes = "DT_FLOAT, DT_FLOAT";
        String outputRanks = "0, 0";

        TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
                outputNames, outputTypes, outputRanks,
                new Properties(), 5);
        TypeInformation[] types = new TypeInformation[2];
        types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
        types[1] = BasicTypeInfo.FLOAT_TYPE_INFO;

        RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames.split(","));
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        streamEnv.setParallelism(1);
        tableEnv.createTemporaryTable("source", TableDescriptor
                .forConnector("TableDebugRow")
                .schema(Schema.newBuilder()
                        .column("a", DataTypes.FLOAT())
                        .column("b", DataTypes.FLOAT())
                        .build())
                .build());
        tableEnv.registerFunction("inference", predictUDTF);

        tableEnv.createTemporaryTable("sink", TableDescriptor
                .forConnector("print")
                .schema(TypeUtil.rowTypeInfoToSchema(typeInfo))
                .build());
        tableEnv.executeSql(
                "INSERT INTO sink SELECT d, e FROM source, LATERAL TABLE(inference(a, b)) as T(d, e)")
                .getJobClient().get()
                .getJobExecutionResult().get();
    }

    @Test
    public void eval3() throws Exception {
        String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath() + "export";
        String inputNames = "a,b";
        String inputTypes = "DT_FLOAT, DT_FLOAT";
        String inputRanks = "1, 1";
        String outputNames = "d,a";
        String outputTypes = "DT_FLOAT, DT_FLOAT";
        String outputRanks = "1, 1";
        TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
                outputNames, outputTypes, outputRanks,
                new Properties(), 5);
        TypeInformation[] types = new TypeInformation[2];
        types[0] = TypeInformation.of(float[].class);
        types[1] = TypeInformation.of(float[].class);

        RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames.split(","));
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        streamEnv.setParallelism(1);
        tableEnv.createTemporaryTable("source", TableDescriptor
                .forConnector("TableDebugRow")
                .option(TableDebugRowOptions.CONNECTOR_RANK_OPTION, 1)
                .schema(Schema.newBuilder()
                        .column("a", DataTypes.ARRAY(DataTypes.FLOAT()))
                        .column("b", DataTypes.ARRAY(DataTypes.FLOAT()))
                        .build())
                .build());

        tableEnv.registerFunction("inference", predictUDTF);

        tableEnv.createTemporaryTable("sink", TableDescriptor
                .forConnector("print")
                .schema(TypeUtil.rowTypeInfoToSchema(typeInfo))
                .build());
        tableEnv.executeSql(
                "INSERT INTO sink SELECT d, e FROM source, LATERAL TABLE(inference(a, b)) as T(d, e)")
                .getJobClient().get()
                .getJobExecutionResult().get();
    }

    @Test
    public void eval4() throws Exception {
        String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath() + "export2";
        String inputNames = "a,b,e";
        String inputTypes = "DT_FLOAT, DT_FLOAT, DT_STRING";
        String inputRanks = "1, 1, 1";
        String outputNames = "d,a,e4";
        String outputTypes = "DT_FLOAT, DT_FLOAT, DT_STRING";
        String outputRanks = "1,1,1";
        TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
                outputNames, outputTypes, outputRanks,
                new Properties(), 5);
        TypeInformation[] types = new TypeInformation[3];
        types[0] = TypeInformation.of(float[].class);
        types[1] = TypeInformation.of(float[].class);
        types[2] = TypeInformation.of(String[].class);

        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        streamEnv.setParallelism(1);
        Schema sourceTableSchema = Schema.newBuilder()
                .column("a", DataTypes.ARRAY(DataTypes.FLOAT()))
                .column("b", DataTypes.ARRAY(DataTypes.FLOAT()))
                .column("c", DataTypes.ARRAY(DataTypes.STRING()))
                .build();

        tableEnv.createTemporaryTable("source", TableDescriptor
                .forConnector("TableDebugRow")
                .option(TableDebugRowOptions.CONNECTOR_RANK_OPTION, 1)
                .option(TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION, true)
                .schema(sourceTableSchema)
                .build());

        tableEnv.registerFunction("inference", predictUDTF);

        Schema sinkTableSchema = Schema.newBuilder()
                .column("d", DataTypes.ARRAY(DataTypes.FLOAT()))
                .column("f", DataTypes.ARRAY(DataTypes.FLOAT()))
                .column("h", DataTypes.ARRAY(DataTypes.STRING()))
                .build();

        tableEnv.createTemporaryTable("sink", TableDescriptor
                .forConnector("print")
                .schema(sinkTableSchema)
                .build());

        tableEnv.executeSql(
                "INSERT INTO sink SELECT d, f, h FROM source, LATERAL TABLE(inference(a, b, c)) as T(d, f, h)")
                .getJobClient().get()
                .getJobExecutionResult().get();
    }

    @Test
    public void eval5() throws Exception {
        String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath() + "export2";
        String inputNames = "a,b,e";
        String inputTypes = "DT_FLOAT, DT_FLOAT, DT_STRING";
        String inputRanks = "2, 2, 2";
        String outputNames = "d,a,e4";
        String outputTypes = "DT_FLOAT, DT_FLOAT, DT_STRING";
        String outputRanks = "2,2,2";
        TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
                outputNames, outputTypes, outputRanks,
                new Properties(), 5);
        TypeInformation[] types = new TypeInformation[3];
        types[0] = TypeInformation.of(float[][].class);
        types[1] = TypeInformation.of(float[][].class);
        types[2] = TypeInformation.of(String[][].class);

        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        streamEnv.setParallelism(1);
        Schema sourceTableSchema = Schema.newBuilder()
                .column("a", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())))
                .column("b", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())))
                .column("c", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.STRING())))
                .build();

        tableEnv.createTemporaryTable("source", TableDescriptor
                .forConnector("TableDebugRow")
                .option(TableDebugRowOptions.CONNECTOR_RANK_OPTION, 2)
                .option(TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION, true)
                .schema(sourceTableSchema)
                .build());

        tableEnv.registerFunction("inference", predictUDTF);

        Schema sinkTableSchema = Schema.newBuilder()
                .column("d", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())))
                .column("f", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())))
                .column("h", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.STRING())))
                .build();

        tableEnv.createTemporaryTable("sink", TableDescriptor
                .forConnector("print")
                .schema(sinkTableSchema)
                .build());
        tableEnv.executeSql(
                "INSERT INTO sink SELECT d, f, h FROM source, LATERAL TABLE(inference(a, b, c)) as T(d, f, h)")
                .getJobClient().get()
                .getJobExecutionResult().get();
    }
}