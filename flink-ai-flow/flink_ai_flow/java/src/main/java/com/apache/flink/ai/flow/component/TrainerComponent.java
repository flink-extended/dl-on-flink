/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.apache.flink.ai.flow.component;

import com.apache.flink.ai.flow.ComponentContext;
import com.apache.flink.ai.flow.ConstantConfig;
import com.apache.flink.ai.flow.common.ReflectUtil;
import com.apache.flink.ai.flow.node.BaseNode;
import com.apache.flink.ai.flow.node.TrainerNode;
import org.apache.flink.ml.api.core.Estimator;
import org.apache.flink.ml.api.core.Model;
import org.apache.flink.ml.api.misc.param.ParamInfoFactory;
import org.apache.flink.table.api.Table;

import java.util.ArrayList;
import java.util.List;

/**
 * translate predictor node to code
 */
public class TrainerComponent implements Component {
    @Override
    public List<Table> translate(ComponentContext context, BaseNode node, List<Table> inputs) throws Exception {
        TrainerNode trainerNode = (TrainerNode) node;
        Class[] classes = new Class[1];
        classes[0] = ComponentContext.class;
        Object[] objects = new Object[1];
        objects[0] = context;
        Estimator estimator = ReflectUtil.createInstance(trainerNode.getClassName(), classes, objects);
        //set prams
        estimator.set(ParamInfoFactory.createParamInfo(ConstantConfig.EXECUTION_MODE_IS_STREAM, Boolean.class).build(),
                context.isStream());
        estimator.set(ParamInfoFactory.createParamInfo(ConstantConfig.NODE_CONFIG, TrainerNode.class).build(),
                trainerNode);
        estimator.set(ParamInfoFactory.createParamInfo(ConstantConfig.WORKFLOW_EXECUTION_ID, Long.class).build(),
                context.getWorkflowExecutionId());
        Model model = estimator.fit(context.getTableEnv(), inputs.get(0));
        List<Table> resultList = new ArrayList<>();
        return resultList;
    }
}
