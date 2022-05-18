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

package org.flinkextended.flink.ml.data;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.data.impl.DataBridgeImpl;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.ReflectUtil;

/** a factory for DataBridge. */
public class DataBridgeFactory {
    public static DataBridge getDataBridge(MLContext mlContext) throws Exception {
        String className =
                mlContext
                        .getProperties()
                        .getOrDefault(
                                MLConstants.DATA_BRIDGE_CLASS,
                                DataBridgeImpl.class.getCanonicalName());
        Class[] classes = new Class[1];
        classes[0] = MLContext.class;
        Object[] objects = new Object[1];
        objects[0] = mlContext;
        return ReflectUtil.createInstance(className, classes, objects);
    }
}
