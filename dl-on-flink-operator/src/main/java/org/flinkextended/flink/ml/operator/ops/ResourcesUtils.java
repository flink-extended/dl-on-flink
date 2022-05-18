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

package org.flinkextended.flink.ml.operator.ops;

import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.externalresource.ExternalResourceInfo;
import org.apache.flink.api.common.functions.RuntimeContext;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

/** ResourceUtils get resource profile of the node. */
public class ResourcesUtils {

    public static void parseGpuInfo(RuntimeContext runtimeContext, MLConfig mlConfig) {
        mlConfig.getProperties().put(MLConstants.GPU_INFO, parseGpuInfo(runtimeContext));
    }

    public static String parseGpuInfo(RuntimeContext runtimeContext) {
        Set<ExternalResourceInfo> gpuInfo = runtimeContext.getExternalResourceInfos("gpu");
        if (gpuInfo != null && gpuInfo.size() > 0) {
            List<String> indexList = new ArrayList<>();
            for (ExternalResourceInfo gpu : gpuInfo) {
                if (gpu.getProperty("index").isPresent()) {
                    indexList.add(gpu.getProperty("index").get());
                }
            }
            Collections.sort(indexList);
            return String.join(",", indexList);
        } else {
            return "";
        }
    }
}
