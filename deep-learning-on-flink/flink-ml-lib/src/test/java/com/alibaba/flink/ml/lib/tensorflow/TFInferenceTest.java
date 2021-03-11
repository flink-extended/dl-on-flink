package com.alibaba.flink.ml.lib.tensorflow;

import org.apache.flink.types.Row;

import com.alibaba.flink.ml.lib.tensorflow.util.ShellExec;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.tensorflow.proto.framework.DataType;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class TFInferenceTest {

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
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void inferenceTest() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export";
		String[] inputNames = {"a", "b"};
		DataType[] inputTypes = {DataType.DT_FLOAT, DataType.DT_FLOAT};
		int[] inputRanks = {0, 0};
		String[] outputNames = {"d"};
		DataType[] outputTypes = {DataType.DT_FLOAT};
		int[] outputRanks = {0};

		TFInference tfInference = new TFInference(modelDir,inputNames, inputTypes, inputRanks,
				outputNames, outputTypes, outputRanks, new Properties());
		List<Object[]> input = new ArrayList<>();
		for(int i = 1; i < 4; i++){
			Object[] r = new Object[2];
			r[0] = 1.0f * i;
			r[1] = 2.0f * i;
			input.add(r);
		}
		Row[] results = tfInference.inference(input);
		for (Row r: results){
			System.out.println(r);
		}
		tfInference.close();
	}
}