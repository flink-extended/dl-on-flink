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

package org.flinkextended.flink.ml.tensorflow.hooks;

import org.flinkextended.flink.ml.operator.hook.FlinkOpHook;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Dummy hook for unit test. */
public class DebugHook implements FlinkOpHook {
    private static final Logger LOG = LoggerFactory.getLogger(DebugHook.class);

    public DebugHook() {}

    @Override
    public void open() throws Exception {
        LOG.info("DebugHook open");
    }

    @Override
    public void close() throws Exception {
        LOG.info("DebugHook close");
    }
}
