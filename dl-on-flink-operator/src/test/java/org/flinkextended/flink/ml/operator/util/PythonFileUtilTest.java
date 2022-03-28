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

package org.flinkextended.flink.ml.operator.util;

import org.flinkextended.flink.ml.cluster.MLConfig;

import org.apache.flink.api.common.cache.DistributedCache;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import org.junit.Test;

import java.io.IOException;
import java.util.List;

import static org.flinkextended.flink.ml.util.DummyContext.createDummyMLConfig;
import static org.junit.Assert.assertEquals;

/** Unit test for {@link PythonFileUtil}. */
public class PythonFileUtilTest {

    @Test
    public void testRegisterPythonLibFilesWithoutScheme() throws IOException {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        final MLConfig mlConfig = createDummyMLConfig();
        mlConfig.setPythonFiles(new String[] {"/tmp/test.py"});
        PythonFileUtil.registerPythonFiles(env, mlConfig);

        final List<Tuple2<String, DistributedCache.DistributedCacheEntry>> cachedFiles =
                env.getCachedFiles();
        assertEquals(1, cachedFiles.size());
        assertEquals("/tmp/test.py", cachedFiles.get(0).f1.filePath);
        assertEquals("test.py", cachedFiles.get(0).f0);
    }

    @Test
    public void testRegisterPythonLibFilesSameFileTwice() throws IOException {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        PythonFileUtil.registerPythonLibFilesIfNotExist(env, "/tmp/test.py");
        PythonFileUtil.registerPythonLibFilesIfNotExist(env, "/tmp/test.py");

        final List<Tuple2<String, DistributedCache.DistributedCacheEntry>> cachedFiles =
                env.getCachedFiles();
        assertEquals(1, cachedFiles.size());
        assertEquals("/tmp/test.py", cachedFiles.get(0).f1.filePath);
        assertEquals("test.py", cachedFiles.get(0).f0);
    }

    @Test(expected = IllegalStateException.class)
    public void testRegisterPythonLibFilesSameFileTwiceWithDifferentPath() throws IOException {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        PythonFileUtil.registerPythonLibFilesIfNotExist(env, "/tmp/test.py");
        PythonFileUtil.registerPythonLibFilesIfNotExist(env, "/tmp1/test.py");
    }
}
