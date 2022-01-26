package org.flinkextended.flink.ml.tensorflow.cluster;

import org.flinkextended.flink.ml.cluster.BaseEventReporter;
import org.flinkextended.flink.ml.cluster.master.AMEvent;
import org.flinkextended.flink.ml.cluster.master.AMEventType;
import org.flinkextended.flink.ml.cluster.master.meta.AMMeta;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServiceImpl;
import org.flinkextended.flink.ml.cluster.statemachine.StateMachine;
import org.flinkextended.flink.ml.proto.AMStatus;
import org.flinkextended.flink.ml.util.DummyContext;
import org.junit.Test;
import org.mockito.Mockito;

import static org.junit.Assert.*;

public class TFAMStateMachineImplTest {

	@Test
	public void testBuildStateMachine() {
		final MLContext mlContext = DummyContext.createDummyMLContext();
		final AMMeta amMeta = Mockito.mock(AMMeta.class);
		final TFAMStateMachineImpl stateMachine = new TFAMStateMachineImpl(Mockito.mock(AppMasterServiceImpl.class),
				amMeta, mlContext, Mockito.mock(BaseEventReporter.class));
		final StateMachine<AMStatus, AMEventType, AMEvent> machine =
				stateMachine.buildStateMachine(mlContext, amMeta);
		assertEquals(AMStatus.AM_UNKNOW, machine.getCurrentState());
	}
}