package org.flinkextended.flink.ml.tensorflow.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

import static org.junit.Assert.*;

public class TensorBoardPythonRunnerTest {

	@Test
	public void testRunScript() throws IOException {
		final MLContext mlContext = DummyContext.createDummyMLContext();
		mlContext.setPythonDir(Paths.get("/tmp"));
		mlContext.setPythonFiles(new String[]{"tensorboard.py"});
		final TensorBoardPythonRunner tensorboardRunner = Mockito.spy(new TensorBoardPythonRunner(mlContext));
		ArgumentCaptor<ProcessBuilder> captor = ArgumentCaptor.forClass(ProcessBuilder.class);
		Mockito.doNothing().when(tensorboardRunner).runProcess(captor.capture());
		tensorboardRunner.runScript();
		final List<String> command = captor.getValue().command();
		assertEquals(5, command.size());
		assertEquals("python", command.get(0));
		assertEquals("/tmp/tensorboard.py", command.get(1));
	}
}