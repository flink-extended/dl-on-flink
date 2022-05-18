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

package org.flinkextended.flink.ml.operator.client;

import org.flinkextended.flink.ml.cluster.MLConfig;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.TableEnvironment;

/** Utils for Table unit test. */
public class TableTestUtil {

    public static void execTableJobCustom(
            MLConfig mlConfig,
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet)
            throws Exception {
        statementSet.execute().getJobClient().get().getJobExecutionResult().get();
    }
}
