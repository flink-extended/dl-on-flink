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

import org.flinkextended.flink.ml.cluster.master.AMEvent;
import org.flinkextended.flink.ml.cluster.master.AMEventType;
import org.flinkextended.flink.ml.cluster.master.AMTransition;
import org.flinkextended.flink.ml.cluster.master.AbstractAMStateMachine;
import org.flinkextended.flink.ml.cluster.role.PsRole;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.cluster.statemachine.InvalidStateTransitionException;
import org.flinkextended.flink.ml.cluster.statemachine.transition.SingleArcTransition;
import org.flinkextended.flink.ml.proto.FinishNodeRequest;
import org.flinkextended.flink.ml.proto.MLClusterDef;
import org.flinkextended.flink.ml.proto.MLJobDef;
import org.flinkextended.flink.ml.proto.RegisterNodeRequest;
import org.flinkextended.flink.ml.tensorflow.client.TFClusterConfig;
import org.flinkextended.flink.ml.util.ProtoUtil;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Map;

/** tensorflow application master special transitions. */
public class TFTransitions {
    private static final Logger LOG = LoggerFactory.getLogger(TFTransitions.class);

    /** tensorflow cluster in batch mode, if worker 0 finish then all cluster finish. */
    public static class FinishNode extends AMTransition
            implements SingleArcTransition<AbstractAMStateMachine, AMEvent> {

        public FinishNode(AbstractAMStateMachine stateMachine) {
            super(stateMachine);
        }

        @Override
        public void transition(AbstractAMStateMachine amStateMachine, AMEvent amEvent)
                throws InvalidStateTransitionException {
            FinishNodeRequest request = (FinishNodeRequest) amEvent.getMessage();
            LOG.info("Finish Node:" + ProtoUtil.protoToJson(request.getNodeSpec()));
            try {
                if (eventReporter != null) {
                    eventReporter.nodeFinish(nodeSpec2Str(request.getNodeSpec()));
                }
                amMeta.saveFinishNodeSpec(request.getNodeSpec());
            } catch (IOException e) {
                e.printStackTrace();
                throw new InvalidStateTransitionException(getInternalState(), amEvent);
            }
            if (isTensorboardFinish(request)) {
                return;
            }
            boolean workerZeroFinish = isWorkerZeroFinish(request);
            if (workerZeroFinish && mlContext.isBatchMode()) {
                LOG.info("worker 0 finish and send finish cluster event!");
                AMEvent finishEvent =
                        new AMEvent(AMEventType.FINISH_CLUSTER, "", request.getVersion());
                amStateMachine.sendEvent(finishEvent);
            } else {
                Map<String, Integer> remainJobNumMap = updateRemainJobNum(amEvent);
                int numRemainWorker = remainJobNumMap.getOrDefault(new WorkerRole().name(), 0);
                if (0 == numRemainWorker && mlContext.isStreamMode()) {
                    LOG.info("send finish cluster event!");
                    AMEvent finishEvent =
                            new AMEvent(AMEventType.FINISH_CLUSTER, "", request.getVersion());
                    amStateMachine.sendEvent(finishEvent);
                }
            }
        }

        private boolean isTensorboardFinish(FinishNodeRequest request) {
            return request.getNodeSpec()
                    .getRoleName()
                    .equals(TFClusterConfig.TENSORBOARD_NODE_TYPE);
        }

        private static boolean isWorkerZeroFinish(FinishNodeRequest request) {
            return request.getNodeSpec().getRoleName().equals(new WorkerRole().name())
                    && 0 == request.getNodeSpec().getIndex();
        }
    }

    /** tensorflow application master only handle worker,ps node register. */
    public static class RegisterNode extends AMTransition
            implements SingleArcTransition<AbstractAMStateMachine, AMEvent> {

        public RegisterNode(AbstractAMStateMachine stateMachine) {
            super(stateMachine);
        }

        @Override
        public synchronized void transition(AbstractAMStateMachine amStateMachine, AMEvent amEvent)
                throws InvalidStateTransitionException {
            RegisterNodeRequest request = (RegisterNodeRequest) amEvent.getMessage();
            LOG.info("Register Node:" + ProtoUtil.protoToJson(request.getNodeSpec()));
            try {
                if (eventReporter != null) {
                    eventReporter.nodeRegister(nodeSpec2Str(request.getNodeSpec()));
                }
                MLClusterDef clusterDef = amMeta.saveNodeSpec(request.getNodeSpec());
                int workerNum = 0;
                int psNum = 0;
                for (MLJobDef jobDef : clusterDef.getJobList()) {
                    if (jobDef.getName().equals(new WorkerRole().name())) {
                        workerNum = jobDef.getTasksCount();
                    } else if (jobDef.getName().equals(new PsRole().name())) {
                        psNum = jobDef.getTasksCount();
                    }
                }
                Map<String, Integer> remainJobNumMap = updateRemainJobNum(amEvent);
                int remainWorkerNum =
                        remainJobNumMap.get(new WorkerRole().name()) != null
                                ? remainJobNumMap.get(new WorkerRole().name())
                                : 0;
                int remainPsNum =
                        remainJobNumMap.get(new PsRole().name()) != null
                                ? remainJobNumMap.get(new PsRole().name())
                                : 0;
                boolean flag = false;
                if (workerNum == remainWorkerNum && psNum == remainPsNum) {
                    flag = true;
                }
                if (flag
                        && (!request.getNodeSpec()
                                .getRoleName()
                                .equals(new TensorBoardRole().name()))) {
                    long version = request.getVersion();
                    AMEvent completeEvent = new AMEvent(AMEventType.COMPLETE_CLUSTER, "", version);
                    LOG.info("put complete event to state machine:" + version);
                    stateMachine.sendEvent(completeEvent);
                }
            } catch (IOException e) {
                e.printStackTrace();
                throw new InvalidStateTransitionException(getInternalState(), amEvent);
            }
        }
    }
}
