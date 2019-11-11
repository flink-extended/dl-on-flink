package com.alibaba.flink.ml.lib.tensorflow;

import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;

import com.alibaba.flink.ml.lib.tensorflow.table.TableDebugRowSink;
import com.alibaba.flink.ml.lib.tensorflow.table.TableDebugRowSource;
import com.alibaba.flink.ml.lib.tensorflow.util.ShellExec;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.util.HashMap;

import static org.junit.Assert.*;

public class TFPredictUDTFTest {

	@Before
	public void setUp() throws Exception {
		String pythonScriptPath = this.getClass().getClassLoader().getResource("").getPath()
				+ "../../src/test/python/";
		String pythonScript = pythonScriptPath + "add_saved_model.py";
		String modelDir = this.getClass().getClassLoader().getResource("").getPath()+"export";
		File f = new File(modelDir);
		if(!f.exists()) {
			Assert.assertTrue(ShellExec.run("python " + pythonScript));
		}
		String pythonScript2 = pythonScriptPath + "build_model.py";
		String modelDir2 = this.getClass().getClassLoader().getResource("").getPath()+"export2";
		File f2 = new File(modelDir2);
		if(!f2.exists()) {
			Assert.assertTrue(ShellExec.run("python " + pythonScript2));
		}
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void eval() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export";
		String[] inputNames = {"a", "b"};
		String[] inputTypes = {"FLOAT", "FLOAT"};
		String[] outputNames = {"d"};
		String[] outputTypes = {"FLOAT"};
		TFPredictUDTF predictUDTF = new TFPredictUDTF(modelDir, inputNames, inputTypes, outputNames,outputTypes,
				new HashMap<>(), 5);
		TypeInformation[] types = new TypeInformation[1];
		types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
		RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames);

		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
		streamEnv.setParallelism(1);
		TableDebugRowSource tableDebugRowSource = new TableDebugRowSource();
		tableEnv.registerTableSource("source", tableDebugRowSource);
		tableEnv.registerFunction("predict", predictUDTF);

		tableEnv.registerTableSink("sink", new TableDebugRowSink(typeInfo));
		tableEnv.sqlUpdate(
				"INSERT INTO sink SELECT d FROM source, LATERAL TABLE(predict(a, b)) as T(d)");
		tableEnv.execute("job");
	}

	@Test
	public void eval2() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export";
		String[] inputNames = {"a", "b"};
		String[] inputTypes = {"FLOAT", "FLOAT"};
		String[] outputNames = {"d", "a"};
		String[] outputTypes = {"FLOAT", "FLOAT"};
		TFPredictUDTF predictUDTF = new TFPredictUDTF(modelDir, inputNames,inputTypes, outputNames,outputTypes,
				new HashMap<>(), 5);
		TypeInformation[] types = new TypeInformation[2];
		types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
		types[1] = BasicTypeInfo.FLOAT_TYPE_INFO;

		RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames);
		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
		streamEnv.setParallelism(1);
		TableDebugRowSource tableDebugRowSource = new TableDebugRowSource();
		tableEnv.registerTableSource("source", tableDebugRowSource);
		tableEnv.registerFunction("predict", predictUDTF);

		tableEnv.registerTableSink("sink", new TableDebugRowSink(typeInfo));
		tableEnv.sqlUpdate(
				"INSERT INTO sink SELECT d, e FROM source, LATERAL TABLE(predict(a, b)) as T(d, e)");
		tableEnv.execute("job");
	}

	@Test
	public void eval3() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export";
		String[] inputNames = {"a", "b"};
		String[] inputTypes = {"FLOAT_2", "FLOAT_2"};
		String[] outputNames = {"d", "a"};
		String[] outputTypes = {"FLOAT_2", "FLOAT_2"};
		TFPredictUDTF predictUDTF = new TFPredictUDTF(modelDir, inputNames,inputTypes, outputNames,outputTypes,
				new HashMap<>(), 5);
		TypeInformation[] types = new TypeInformation[2];
		types[0] = TypeInformation.of(float[].class);
		types[1] = TypeInformation.of(float[].class);

		RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames);
		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
		streamEnv.setParallelism(1);
		TableDebugRowSource tableDebugRowSource = new TableDebugRowSource(2);
		tableEnv.registerTableSource("source", tableDebugRowSource);
		tableEnv.registerFunction("predict", predictUDTF);

		tableEnv.registerTableSink("sink", new TableDebugRowSink(typeInfo));
		tableEnv.sqlUpdate(
				"INSERT INTO sink SELECT d, e FROM source, LATERAL TABLE(predict(a, b)) as T(d, e)");
//		tableEnv.sqlUpdate(
//				"INSERT INTO sink SELECT a, b FROM source");
		tableEnv.execute("job");
	}
	@Test

	public void eval4() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export2";
		String[] inputNames = {"a", "b", "e"};
		String[] inputTypes = {"FLOAT_2", "FLOAT_2", "STRING_2"};
		String[] outputNames = {"d", "a", "e4"};
		String[] outputTypes = {"FLOAT_2", "FLOAT_2", "STRING_2"};
		TFPredictUDTF predictUDTF = new TFPredictUDTF(modelDir, inputNames,inputTypes, outputNames,outputTypes,
				new HashMap<>(), 5);
		TypeInformation[] types = new TypeInformation[3];
		types[0] = TypeInformation.of(float[].class);
		types[1] = TypeInformation.of(float[].class);
		types[2] = TypeInformation.of(String[].class);

		RowTypeInfo typeInfo = new RowTypeInfo(types, outputNames);
		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
		streamEnv.setParallelism(1);
		TableDebugRowSource tableDebugRowSource = new TableDebugRowSource(2, true);
		tableEnv.registerTableSource("source", tableDebugRowSource);
		tableEnv.registerFunction("predict", predictUDTF);

		tableEnv.registerTableSink("sink", new TableDebugRowSink(typeInfo));
		tableEnv.sqlUpdate(
				"INSERT INTO sink SELECT d, f, h FROM source, LATERAL TABLE(predict(a, b, c)) as T(d, f, h)");
//		tableEnv.sqlUpdate(
//				"INSERT INTO sink SELECT a, b, c FROM source");
		tableEnv.execute("job");
	}

}