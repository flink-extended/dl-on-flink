/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.tensorflow.cluster;

import org.flinkextended.flink.ml.cluster.BaseEventReporter;
import org.flinkextended.flink.ml.cluster.master.AMEvent;
import org.flinkextended.flink.ml.cluster.master.AMEventType;
import org.flinkextended.flink.ml.cluster.master.meta.AMMeta;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServiceImpl;
import org.flinkextended.flink.ml.cluster.statemachine.InvalidStateTransitionException;
import org.flinkextended.flink.ml.proto.AMStatus;
import org.flinkextended.flink.ml.proto.FinishNodeRequest;
import org.flinkextended.flink.ml.proto.MLClusterDef;
import org.flinkextended.flink.ml.proto.MLJobDef;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.proto.RegisterNodeRequest;
import org.flinkextended.flink.ml.util.DummyContext;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.when;

/** Unit test for {@link TFTransitions}. */
public class TFTransitionsTest {

    private TFAMStateMachineImpl stateMachine;
    private AMMeta amMeta;
    private MLContext mlContext;

    @Before
    public void setUp() throws Exception {
        mlContext = Mockito.spy(DummyContext.createDummyMLContext());
        amMeta = Mockito.mock(AMMeta.class);

        stateMachine =
                new TFAMStateMachineImpl(
                        Mockito.mock(AppMasterServiceImpl.class),
                        amMeta,
                        mlContext,
                        Mockito.mock(BaseEventReporter.class));
        stateMachine.sendEvent(new AMEvent(AMEventType.INTI_AM_STATE, null, 0));
        waitUntilState(AMStatus.AM_INIT);
    }

    @After
    public void tearDown() throws Exception {
        stateMachine.close();
    }

    @Test
    public void testFinishNodeTransition()
            throws InvalidStateTransitionException, IOException, InterruptedException {
        stateMachine.sendEvent(new AMEvent(AMEventType.COMPLETE_CLUSTER, null, 0));
        waitUntilState(AMStatus.AM_RUNNING);

        when(mlContext.isStreamMode()).thenReturn(true);
        final TFTransitions.FinishNode finishNode = new TFTransitions.FinishNode(stateMachine);
        when(amMeta.restoreFinishClusterDef())
                .thenReturn(
                        MLClusterDef.newBuilder()
                                .addJob(MLJobDef.newBuilder().setName("worker").build())
                                .build());
        finishNode.transition(
                stateMachine,
                new AMEvent(AMEventType.FINISH_NODE, FinishNodeRequest.getDefaultInstance(), 0));
        when(amMeta.restoreFinishClusterDef())
                .thenReturn(
                        MLClusterDef.newBuilder()
                                .addJob(
                                        MLJobDef.newBuilder()
                                                .setName("worker")
                                                .putTasks(0, NodeSpec.newBuilder().build())
                                                .build())
                                .build());
        finishNode.transition(
                stateMachine,
                new AMEvent(AMEventType.FINISH_NODE, FinishNodeRequest.getDefaultInstance(), 0));
        waitUntilState(AMStatus.AM_FINISH);
    }

    @Test
    public void testRegisterNodeTransition()
            throws InvalidStateTransitionException, IOException, InterruptedException {
        final TFTransitions.RegisterNode registerNode =
                new TFTransitions.RegisterNode(stateMachine);
        final RegisterNodeRequest registerNodeRequest =
                RegisterNodeRequest.newBuilder()
                        .setNodeSpec(NodeSpec.newBuilder().setRoleName("worker").build())
                        .build();

        when(amMeta.saveNodeSpec(any(NodeSpec.class)))
                .thenReturn(
                        MLClusterDef.newBuilder()
                                .addJob(
                                        MLJobDef.newBuilder()
                                                .setName("worker")
                                                .putTasks(0, NodeSpec.newBuilder().build())
                                                .build())
                                .build());
        when(amMeta.restoreFinishClusterDef())
                .thenReturn(
                        MLClusterDef.newBuilder()
                                .addJob(MLJobDef.newBuilder().setName("worker").build())
                                .build());

        registerNode.transition(
                stateMachine, new AMEvent(AMEventType.REGISTER_NODE, registerNodeRequest, 0));
        waitUntilState(AMStatus.AM_RUNNING);
    }

    @Test
    public void testFinishNodeTransitionWorkerZeroFinish()
            throws InvalidStateTransitionException, IOException, InterruptedException {
        stateMachine.sendEvent(new AMEvent(AMEventType.COMPLETE_CLUSTER, null, 0));
        waitUntilState(AMStatus.AM_RUNNING);

        when(mlContext.isBatchMode()).thenReturn(true);
        final TFTransitions.FinishNode finishNode = new TFTransitions.FinishNode(stateMachine);
        when(amMeta.restoreFinishClusterDef())
                .thenReturn(
                        MLClusterDef.newBuilder()
                                .addJob(MLJobDef.newBuilder().setName("worker").build())
                                .build());
        finishNode.transition(
                stateMachine,
                new AMEvent(
                        AMEventType.FINISH_NODE,
                        FinishNodeRequest.newBuilder()
                                .setNodeSpec(NodeSpec.newBuilder().setRoleName("worker").build())
                                .build(),
                        0));
        waitUntilState(AMStatus.AM_FINISH);
    }

    private void waitUntilState(AMStatus status) throws InterruptedException {
        while (stateMachine.getInternalState() != status) {
            Thread.sleep(100);
        }
    }
}
