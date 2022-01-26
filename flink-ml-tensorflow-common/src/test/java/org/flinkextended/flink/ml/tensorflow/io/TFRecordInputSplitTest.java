package org.flinkextended.flink.ml.tensorflow.io;

import org.apache.hadoop.fs.Path;
import org.junit.Before;
import org.junit.Test;


import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

public class TFRecordInputSplitTest {

	private TFRecordInputSplit split;
	private String filePath;
	private int num;

	@Before
	public void setUp() throws Exception {
		filePath = "/tmp/data.tfrecord";
		num = 0;
		split = new TFRecordInputSplit(num, filePath);
	}

	@Test
	public void testGetSplitNumber() {
		assertEquals(0, split.getSplitNumber());
	}

	@Test
	public void testGetPath() {
		assertEquals(new Path("/tmp/data.tfrecord"), split.getPath());
	}

	@Test
	public void testGetEpochs() {
		assertEquals(0, split.getEpochs());
		split.setEpochs(1);
		assertEquals(1, split.getEpochs());
	}

	@Test
	public void testGetIndex() {
		assertEquals(0, split.getIndex());
	}

	@Test
	public void testEqual() {
		TFRecordInputSplit mySplit = new TFRecordInputSplit(num, filePath);
		assertEquals(split, mySplit);
		assertEquals(split.hashCode(), mySplit.hashCode());

		mySplit = new TFRecordInputSplit(num + 1, filePath);
		assertNotEquals(split, mySplit);
		assertNotEquals(split, 1);
	}

	@Test
	public void testToString() {
		assertTrue(split.toString().contains("TFRecordInputSplit"));
	}
}