package com.alibaba.flink.ml.cluster.storage;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.*;

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