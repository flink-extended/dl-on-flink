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

package org.flinkextended.flink.ml.cluster.storage;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

/** Unit test for {@link MemoryStorageImpl}. */
public class MemoryStorageImplTest {

    private MemoryStorageImpl storage;

    @Before
    public void setUp() throws Exception {
        storage = new MemoryStorageImpl();
    }

    @Test
    public void testMemoryStorageImpl() throws IOException {
        storage.setValue("key", "value".getBytes());
        storage.setValue("key1", "value1".getBytes());
        assertEquals("value", new String(storage.getValue("key")));
        assertEquals("value1", new String(storage.getValue("key1")));
        assertTrue(storage.exists("key"));
        assertFalse(storage.exists("non-exist"));
        assertNull(storage.getValue("non-exist"));

        storage.removeValue("key");
        assertNull(storage.getValue("key"));

        assertNull(storage.listChildren("."));

        storage.clear();
        assertNull(storage.getValue("key1"));
    }
}
