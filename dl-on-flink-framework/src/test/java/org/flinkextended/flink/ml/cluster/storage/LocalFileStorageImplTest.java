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

package org.flinkextended.flink.ml.cluster.storage;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

public class LocalFileStorageImplTest {

    private LocalFileStorageImpl storage;
    private Path tempDirectory;

    @Before
    public void setUp() throws Exception {
        //        tempDirectory = Files.createTempDirectory("");
        storage = new LocalFileStorageImpl("/tmp");
    }

    @After
    public void tearDown() throws Exception {
        storage.clear();
    }

    @Test
    public void testCreateMultipleStorage() {
        final LocalFileStorageImpl myStorage = new LocalFileStorageImpl("/tmp");
        storage.clear();
        myStorage.clear();
    }

    @Test
    public void testGetSetValue() throws IOException {
        assertNull(storage.getValue("am_address"));
        storage.setValue("am_address", "v1".getBytes(StandardCharsets.UTF_8));
        assertEquals("v1", new String(storage.getValue("am_address")));
        storage.setValue("am_address", "v2".getBytes(StandardCharsets.UTF_8));
        assertEquals("v2", new String(storage.getValue("am_address")));
    }

    @Test
    public void testRemoveValue() throws IOException {
        storage.setValue("k1", "v1".getBytes(StandardCharsets.UTF_8));
        assertEquals("v1", new String(storage.getValue("k1")));
        storage.removeValue("k1");
        assertNull(storage.getValue("k1"));
    }

    @Test(expected = UnsupportedOperationException.class)
    public void testListChildren() throws IOException {
        storage.listChildren("k1");
    }

    @Test
    public void testExists() throws IOException {
        assertFalse(storage.exists("k1"));
        storage.setValue("k1", "v1".getBytes(StandardCharsets.UTF_8));
        assertTrue(storage.exists("k1"));
    }

    @Test
    public void testClear() throws IOException {
        storage.setValue("k1", "v1".getBytes(StandardCharsets.UTF_8));
        storage.setValue("k2", "v2".getBytes(StandardCharsets.UTF_8));
        storage.clear();
        assertFalse(storage.exists("k1"));
        assertFalse(storage.exists("k2"));
    }
}
