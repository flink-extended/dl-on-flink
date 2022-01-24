package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.data.DataExchange;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.FileUtil;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;
import com.google.common.base.Joiner;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.types.Row;
import org.apache.flink.types.RowKind;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.mockito.internal.util.reflection.Whitebox;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

import java.net.URL;
import java.util.Arrays;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class JavaInferenceRunnerTest {
	private FutureTask<Void> nodeFuture;

	private MLContext mlContext;
	private NodeServer nodeServer;


	@Before
	public void setUp() throws Exception {
		mlContext = DummyContext.createDummyMLContext();
		final URL resource = FileUtil.class.getClassLoader().getResource("model/0");
		assertNotNull(resource);
		mlContext.getProperties().put(TFConstants.TF_INFERENCE_EXPORT_PATH, resource.toURI().getPath());
		mlContext.getProperties().put(TFConstants.TF_INFERENCE_INPUT_TENSOR_NAMES, "image");
		mlContext.getProperties().put(TFConstants.TF_INFERENCE_OUTPUT_TENSOR_NAMES, "prediction");
		mlContext.getProperties().put(TFConstants.TF_INFERENCE_OUTPUT_ROW_FIELDS,
				Joiner.on(",").join(new String[] { "prediction" }));
		setExampleCodingType(mlContext);
		startNodeServer();
	}

	@After
	public void tearDown() throws Exception {
		nodeServer.setAmCommand(NodeServer.AMCommand.STOP);
		nodeFuture.get();
	}

	@Test
	public void testJavaInferenceRunner() throws Exception {
		while (nodeServer.getPort() == null) {
			Thread.sleep(1000);
		}
		final RowTypeInfo inRowType = new RowTypeInfo(new TypeInformation[]{ Types.PRIMITIVE_ARRAY(Types.FLOAT) }, new String[]{ "image" });
		final RowTypeInfo outRowTpe = new RowTypeInfo(new TypeInformation[]{ Types.LONG }, new String[]{ "prediction" });
		final JavaInferenceRunner runner = new JavaInferenceRunner("localhost", nodeServer.getPort(),
				inRowType, outRowTpe);

		DataExchange<Row, Row> dataExchange =
				(DataExchange<Row, Row>) Whitebox.getInternalState(runner, "dataExchange");
		dataExchange = Mockito.spy(dataExchange);
		Whitebox.setInternalState(runner, "dataExchange", dataExchange);

		Mockito.when(dataExchange.read(Mockito.anyBoolean())).thenAnswer(new Answer<Row>() {
			private int callCnt = 0;
			@Override
			public Row answer(InvocationOnMock invocation) throws Throwable {
				if (callCnt > 0) {
					return null;
				}
				callCnt++;
				final Row row = new Row(RowKind.INSERT, 1);
				float[] floats = new float[784];
				Arrays.fill(floats, 0.1f);
				row.setField(0, floats);
				return row;
			}
		});

		runner.run();

		ArgumentCaptor<Row> captor = ArgumentCaptor.forClass(Row.class);
		Mockito.verify(dataExchange).write(captor.capture());
		final Row row = captor.getValue();
		assertEquals(1, row.getArity());

		runner.close();
	}

	private void setExampleCodingType(MLContext mlContext) {
		mlContext.getProperties().put(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getCanonicalName());
		mlContext.getProperties().put(MLConstants.DECODING_CLASS, RowCSVCoding.class.getCanonicalName());
	}

	private FutureTask<Void> startNodeServer() throws MLException {
		nodeServer = new NodeServer(mlContext, "worker");
		nodeFuture = new FutureTask<>(nodeServer, null);
		Thread thread = new Thread(nodeFuture);
		thread.setDaemon(true);
		thread.start();
		return nodeFuture;
	}
}