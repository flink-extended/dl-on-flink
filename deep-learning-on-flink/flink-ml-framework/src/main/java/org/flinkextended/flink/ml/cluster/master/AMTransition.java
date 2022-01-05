/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.cluster.master;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.proto.MLClusterDef;
import org.flinkextended.flink.ml.proto.MLJobDef;
import org.flinkextended.flink.ml.cluster.BaseEventReporter;
import org.flinkextended.flink.ml.cluster.master.meta.AMMeta;
import org.flinkextended.flink.ml.cluster.statemachine.InvalidStateTransitionException;
import org.flinkextended.flink.ml.proto.AMStatus;
import org.flinkextended.flink.ml.proto.NodeSpec;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Base AM(application master) transition class, handle am event and am state machine state transition.
 * am state machine receive am event then pass to transition to process event.
 */
public class AMTransition {
	protected final AMMeta amMeta;
	protected final MLContext mlContext;
	protected final AMService amService;
	protected final BaseEventReporter eventReporter;
	protected final AbstractAMStateMachine stateMachine;
	protected Map<String, Integer> remainJobNumberMap;

	public AMTransition(AbstractAMStateMachine stateMachine) {
		this.stateMachine = stateMachine;
		this.amMeta = stateMachine.getAMMeta();
		this.mlContext = stateMachine.getMLContext();
		this.amService = stateMachine.getAmService();
		this.eventReporter = stateMachine.getEventReporter();
		this.remainJobNumberMap = new HashMap<>(mlContext.getRoleParallelismMap());
	}

	public AMStatus getInternalState() {
		return stateMachine.getInternalState();
	}

	/**
	 * @param spec cluster node spec.
	 * @return cluster node identity
	 */
	public static String nodeSpec2Str(NodeSpec spec) {
		return spec.getRoleName() + ":" + spec.getIndex();
	}

	/**
	 * update running node information.
	 * @param amEvent application master event.
	 * @return running node information
	 * @throws InvalidStateTransitionException
	 */
	protected Map<String, Integer> updateRemainJobNum(AMEvent amEvent) throws InvalidStateTransitionException {
		MLClusterDef finishCluster = null;
		try {
			finishCluster = amMeta.restoreFinishClusterDef();
		} catch (IOException e) {
			e.printStackTrace();
			throw new InvalidStateTransitionException(getInternalState(), amEvent);
		}
		if (null != finishCluster) {
			for (MLJobDef jobDef : finishCluster.getJobList()) {
				Integer a = mlContext.getRoleParallelismMap().get(jobDef.getName()) - jobDef.getTasksCount();
				remainJobNumberMap.put(jobDef.getName(), a);
			}
		}
		return remainJobNumberMap;
	}

}
