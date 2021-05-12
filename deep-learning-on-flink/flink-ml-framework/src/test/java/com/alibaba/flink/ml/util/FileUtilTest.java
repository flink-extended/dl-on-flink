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

package com.alibaba.flink.ml.util;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public class FileUtilTest {
	private static Logger LOG = LoggerFactory.getLogger(FileUtilTest.class);

	private Path workDir;

	@Before
	public void setUp() throws Exception {
		workDir = Files.createTempDirectory(FileUtilTest.class.getName());
	}

	@Test
	public void parseFileName() throws Exception {
		String fileName = FileUtil.parseFileName("hdfs://hadoop-master:9000/root/tfenv.zip");
		Assert.assertEquals("tfenv.zip", fileName);
		String dirName = FileUtil.getFileNameWithoutExtension(fileName);
		Assert.assertEquals("tfenv", dirName);
	}

	@Test
	public void testDownloadZipToLocal() throws IOException {
		final URL resource = FileUtil.class.getClassLoader().getResource("test-code.zip");
		assertNotNull(resource);
		FileUtil.downLoadZipToLocal(workDir.toAbsolutePath().toString(), resource.toString(), null);
		assertTrue(Files.exists(workDir.resolve("test-code")));
		assertTrue(Files.exists(workDir.resolve("test-code").resolve("code.py")));
	}

	@Test
	public void testDownloadZipWithDifferentUnzipDirName() throws IOException {
		final URL resource = FileUtil.class.getClassLoader().getResource("not-base-dir-name.zip");
		assertNotNull(resource);
		boolean exception = false;
		try {
			FileUtil.downLoadZipToLocal(workDir.toAbsolutePath().toString(), resource.toString(), null);
		} catch (MLException e) {
			// expected
			LOG.error("expected exception", e);
			exception = true;
		}
		assertTrue(exception);

		FileUtil.downLoadZipToLocal(workDir.toAbsolutePath().toString(), resource.toString(), "test-code");
		assertTrue(Files.exists(workDir.resolve("test-code")));
		assertTrue(Files.exists(workDir.resolve("test-code").resolve("code.py")));
	}

	@Test
	public void testDownloadZipToLocalWithoutBaseDir() throws IOException {
		final URL resource = FileUtil.class.getClassLoader().getResource("no-base-dir.zip");
		assertNotNull(resource);
		boolean exception = false;
		try {
			FileUtil.downLoadZipToLocal(workDir.toAbsolutePath().toString(), resource.toString(), null);
		} catch (MLException e) {
			// expected
			LOG.error("expected exception", e);
			exception = true;
		}
		assertTrue(exception);
		exception = false;
		try {
			FileUtil.downLoadZipToLocal(workDir.toAbsolutePath().toString(), resource.toString(), "test-code");
		} catch (MLException e) {
			// expected
			LOG.error("expected exception", e);
			exception = true;
		}
		assertTrue(exception);
	}
}