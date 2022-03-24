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

package org.flinkextended.flink.ml.examples.tensorflow.mnist.ops;

import org.apache.flink.table.factories.TableSourceFactory;
import org.apache.flink.table.sources.TableSource;
import org.apache.flink.types.Row;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;

/** Factory for {@link DelayedTFRSourceFunction}. */
public class DelayedTFRTableSourceFactory implements TableSourceFactory<Row> {
    @Override
    public TableSource<Row> createTableSource(Context context) {
        return null;
    }

    @Override
    public Map<String, String> requiredContext() {
        return Collections.singletonMap(CONNECTOR_TYPE, "DelayedTFRTable");
    }

    @Override
    public List<String> supportedProperties() {
        return Collections.singletonList("*");
    }
}
