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

package org.flinkextended.flink.ml.operator.util;

import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

/** create flink job helper function. */
public class FlinkUtil {

    /**
     * register a table function.
     *
     * @param tableEnv flink TableEnvironment.
     * @param funcName register table function name.
     * @param func table function.
     */
    public static void registerTableFunction(
            TableEnvironment tableEnv, String funcName, TableFunction<Row> func) {
        ((StreamTableEnvironment) tableEnv).registerFunction(funcName, func);
    }
}
