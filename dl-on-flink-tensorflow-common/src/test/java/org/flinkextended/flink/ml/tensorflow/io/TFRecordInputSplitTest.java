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

package org.flinkextended.flink.ml.tensorflow.io;

import org.apache.hadoop.fs.Path;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

public class TFRecordInputSplitTest {

    private TFRecordInputSplit split;
    private String filePath;
    private int num;

    @Before
    public void setUp() throws Exception {
        filePath = "/tmp/data.tfrecord";
        num = 0;
        split = new TFRecordInputSplit(num, filePath);
    }

    @Test
    public void testGetSplitNumber() {
        assertEquals(0, split.getSplitNumber());
    }

    @Test
    public void testGetPath() {
        assertEquals(new Path("/tmp/data.tfrecord"), split.getPath());
    }

    @Test
    public void testGetEpochs() {
        assertEquals(0, split.getEpochs());
        split.setEpochs(1);
        assertEquals(1, split.getEpochs());
    }

    @Test
    public void testGetIndex() {
        assertEquals(0, split.getIndex());
    }

    @Test
    public void testEqual() {
        TFRecordInputSplit mySplit = new TFRecordInputSplit(num, filePath);
        assertEquals(split, mySplit);
        assertEquals(split.hashCode(), mySplit.hashCode());

        mySplit = new TFRecordInputSplit(num + 1, filePath);
        assertNotEquals(split, mySplit);
        assertNotEquals(split, 1);
    }

    @Test
    public void testToString() {
        assertTrue(split.toString().contains("TFRecordInputSplit"));
    }
}
