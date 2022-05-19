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
import org.flinkextended.flink.ml.cluster.statemachine.StateMachine;
import org.flinkextended.flink.ml.proto.AMStatus;
import org.flinkextended.flink.ml.util.DummyContext;

import org.junit.Test;
import org.mockito.Mockito;

import static org.junit.Assert.assertEquals;

/** Unit test for {@link TFAMStateMachineImpl}. */
public class TFAMStateMachineImplTest {

    @Test
    public void testBuildStateMachine() {
        final MLContext mlContext = DummyContext.createDummyMLContext();
        final AMMeta amMeta = Mockito.mock(AMMeta.class);
        final TFAMStateMachineImpl stateMachine =
                new TFAMStateMachineImpl(
                        Mockito.mock(AppMasterServiceImpl.class),
                        amMeta,
                        mlContext,
                        Mockito.mock(BaseEventReporter.class));
        final StateMachine<AMStatus, AMEventType, AMEvent> machine =
                stateMachine.buildStateMachine(mlContext, amMeta);
        assertEquals(AMStatus.AM_UNKNOW, machine.getCurrentState());
    }
}
