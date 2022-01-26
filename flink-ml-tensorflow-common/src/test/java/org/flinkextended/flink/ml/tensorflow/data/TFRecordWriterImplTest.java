package org.flinkextended.flink.ml.tensorflow.data;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.SpscOffHeapQueue;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

import static org.junit.Assert.*;

public class TFRecordWriterImplTest {

	private MLContext mlContext;
	private TFRecordWriterImpl tfRecordWriter;

	@Before
	public void setUp() throws Exception {
		mlContext = DummyContext.createDummyMLContext();
		tfRecordWriter = new TFRecordWriterImpl(mlContext);
	}

	@After
	public void tearDown() throws Exception {
		tfRecordWriter.close();
	}

	@Test
	public void testWrite() throws IOException {
		final SpscOffHeapQueue outputQueue = mlContext.getOutputQueue();
		final SpscOffHeapQueue.QueueInputStream inputStream = new SpscOffHeapQueue.QueueInputStream(outputQueue);
		final TFRecordReader tfRecordReader = new TFRecordReader(inputStream, true);

		byte[] bytes = new byte[]{1, 3, 4};
		tfRecordWriter.write(bytes);

		byte[] read = tfRecordReader.read();
		assertArrayEquals(bytes, read);

		tfRecordWriter.write(bytes, 1, 2);
		read = tfRecordReader.read();
		assertArrayEquals(new byte[]{3, 4}, read);
	}
}