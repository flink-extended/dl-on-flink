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

package org.flinkextended.flink.ml.lib.tensorflow.table.descriptor;

import org.apache.flink.configuration.ConfigOption;

import static org.apache.flink.configuration.ConfigOptions.key;

public class TableDebugRowOptions {
    public static final String CONNECTOR_RANK = "connector.rank";
    public static final ConfigOption<Integer> CONNECTOR_RANK_OPTION =
            key(CONNECTOR_RANK)
                    .intType()
                    .noDefaultValue();
    public static final String CONNECTOR_HAS_STRING = "connector.has-string";

    public static final ConfigOption<Boolean> CONNECTOR_HAS_STRING_OPTION =
            key(CONNECTOR_HAS_STRING)
                    .booleanType()
                    .noDefaultValue();
}
