package com.alibaba.flink.ml.lib.tensorflow;

import org.apache.flink.types.Row;

import com.alibaba.flink.ml.lib.tensorflow.util.ShellExec;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.tensorflow.framework.DataType;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class TFPredictTest {

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
	public void predict() throws Exception{
		String modelDir = "file://" + this.getClass().getClassLoader().getResource("").getPath()+"export";
		String[] inputNames = {"a", "b"};
		DataType[] inputTypes = {DataType.DT_FLOAT, DataType.DT_FLOAT};
		String[] outputNames = {"d"};
		String[] outputTypes = {"FLOAT"};
		int[] dimCounts = {1, 1};
		TFPredict tfPredict = new TFPredict(modelDir, new HashMap<>(),inputNames, inputTypes, outputNames, outputTypes);
		List<Object[]> input = new ArrayList<>();
		for(int i = 1; i < 4; i++){
			Object[] r = new Object[2];
			r[0] = 1.0f * i;
			r[1] = 2.0f * i;
			input.add(r);
		}
		Row[] results = tfPredict.predict(input, dimCounts);
		for (Row r: results){
			System.out.println(r);
		}
		tfPredict.close();
	}
}