package org.flinkextended.flink.ml.tensorflow.data;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.SpscOffHeapQueue;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

import static org.junit.Assert.*;

public class TFRecordReaderImplTest {

	private TFRecordReaderImpl tfRecordReader;
	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		mlContext = DummyContext.createDummyMLContext();
		tfRecordReader = new TFRecordReaderImpl(mlContext);
	}

	@After
	public void tearDown() throws Exception {
		tfRecordReader.close();
	}

	@Test
	public void testTryRead() throws IOException {
		final SpscOffHeapQueue inputQueue = mlContext.getInputQueue();
		final SpscOffHeapQueue.QueueOutputStream output = new SpscOffHeapQueue.QueueOutputStream(inputQueue);
		final DataOutputStream dataOutputStream = new DataOutputStream(output);
		final TFRecordWriter tfRecordWriter = new TFRecordWriter(dataOutputStream);
		tfRecordWriter.write("Hello".getBytes(StandardCharsets.UTF_8));
		assertEquals("Hello", new String(tfRecordReader.tryRead()));
		assertNull(tfRecordReader.tryRead());

		dataOutputStream.close();
		assertNull(tfRecordReader.read());
		assertTrue(tfRecordReader.isReachEOF());
	}
}