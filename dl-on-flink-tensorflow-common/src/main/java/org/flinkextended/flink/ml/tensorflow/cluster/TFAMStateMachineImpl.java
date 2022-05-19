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
import org.flinkextended.flink.ml.cluster.master.AMTransitions;
import org.flinkextended.flink.ml.cluster.master.AbstractAMStateMachine;
import org.flinkextended.flink.ml.cluster.master.meta.AMMeta;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServiceImpl;
import org.flinkextended.flink.ml.cluster.statemachine.StateMachine;
import org.flinkextended.flink.ml.cluster.statemachine.StateMachineBuilder;
import org.flinkextended.flink.ml.proto.AMStatus;

import java.util.EnumSet;

/** tensorflow cluster application master state machine implementation. */
public class TFAMStateMachineImpl extends AbstractAMStateMachine {
    public TFAMStateMachineImpl(
            AppMasterServiceImpl server,
            AMMeta amState,
            MLContext mlContext,
            BaseEventReporter eventReporter) {
        super(server, amState, mlContext, eventReporter);
    }

    @Override
    protected StateMachine<AMStatus, AMEventType, AMEvent> buildStateMachine(
            MLContext mlContext, AMMeta amMeta) {
        StateMachineBuilder<AbstractAMStateMachine, AMStatus, AMEventType, AMEvent>
                stateMachineBuilder =
                        new StateMachineBuilder<
                                        AbstractAMStateMachine, AMStatus, AMEventType, AMEvent>(
                                        AMStatus.AM_UNKNOW)
                                .addTransition(
                                        AMStatus.AM_UNKNOW,
                                        EnumSet.of(
                                                AMStatus.AM_INIT,
                                                AMStatus.AM_RUNNING,
                                                AMStatus.AM_FAILOVER,
                                                AMStatus.AM_FINISH),
                                        AMEventType.INTI_AM_STATE,
                                        new AMTransitions.InitAmState(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_INIT,
                                        AMEventType.REGISTER_NODE,
                                        new TFTransitions.RegisterNode(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_RUNNING,
                                        AMEventType.COMPLETE_CLUSTER,
                                        new AMTransitions.CompleteCluster(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.FAIL_NODE,
                                        new AMTransitions.FailNode(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_FINISH,
                                        AMEventType.STOP_JOB,
                                        new AMTransitions.StopJob(this))
                                .addTransition(
                                        AMStatus.AM_RUNNING,
                                        AMStatus.AM_RUNNING,
                                        AMEventType.FINISH_NODE,
                                        new TFTransitions.FinishNode(this))
                                .addTransition(
                                        AMStatus.AM_RUNNING,
                                        AMStatus.AM_FINISH,
                                        AMEventType.FINISH_CLUSTER,
                                        new AMTransitions.FinishCluster(this))
                                .addTransition(
                                        AMStatus.AM_RUNNING,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.FAIL_NODE,
                                        new AMTransitions.FailNode(this))
                                .addTransition(
                                        AMStatus.AM_RUNNING,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.REGISTER_NODE,
                                        new AMTransitions.FailNode(this))
                                .addTransition(
                                        AMStatus.AM_RUNNING,
                                        AMStatus.AM_FINISH,
                                        AMEventType.STOP_JOB,
                                        new AMTransitions.StopJob(this))
                                .addTransition(
                                        AMStatus.AM_FAILOVER,
                                        AMStatus.AM_INIT,
                                        AMEventType.RESTART_CLUSTER,
                                        new AMTransitions.RestartCluster(this))
                                .addTransition(
                                        AMStatus.AM_FAILOVER,
                                        AMStatus.AM_FINISH,
                                        AMEventType.STOP_JOB,
                                        new AMTransitions.StopJob(this))
                                // some ignore message
                                .addTransition(
                                        AMStatus.AM_FAILOVER,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.FINISH_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_FAILOVER,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.FAIL_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_FAILOVER,
                                        AMStatus.AM_FAILOVER,
                                        AMEventType.REGISTER_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_INIT,
                                        AMEventType.FINISH_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_INIT,
                                        AMStatus.AM_INIT,
                                        AMEventType.RESTART_CLUSTER,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_FINISH,
                                        AMStatus.AM_FINISH,
                                        AMEventType.FINISH_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_FINISH,
                                        AMStatus.AM_FINISH,
                                        AMEventType.STOP_JOB,
                                        new AMTransitions.IgnoreMessage(this))
                                .addTransition(
                                        AMStatus.AM_FINISH,
                                        AMStatus.AM_FINISH,
                                        AMEventType.FINISH_NODE,
                                        new AMTransitions.IgnoreMessage(this))
                                // end
                                .installTopology();
        stateMachine = stateMachineBuilder.make(this);
        return stateMachine;
    }
}
