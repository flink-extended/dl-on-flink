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

import com.google.common.base.Preconditions;
import org.apache.commons.io.FileUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

/**
 * down load zip file from remote file system to local
 */
public class FileUtil {
	private static final Logger LOG = LoggerFactory.getLogger(FileUtil.class);

	/**
	 * parse a path and get file name.
	 * @param path path address.
	 * @return file name.
	 */
	public static String parseFileName(String path) {
		return path.substring(path.lastIndexOf("/") + 1);
	}

	/**
	 * parse a fileName and get dir name.
	 * @param fileName fileName address.
	 * @return dir name.
	 */
	public static String getFileNameWithoutExtension(String fileName) {
		return fileName.substring(0, fileName.lastIndexOf("."));
	}

	/**
	 * download zip file to local address.
	 * @param workDir local address.
	 * @param remotePath remote file address.
	 * @param unzipDirName local dir name.
	 * @throws IOException
	 */
	public static void downLoadZipToLocal(String workDir, String remotePath, String unzipDirName) throws IOException {
		// virtual env is shared across jobs, so we can't use mlContext's temp dir here
		final java.nio.file.Path tempDirectory = Files.createTempDirectory("flink-ml-zip");

		try {
			Path remote = new Path(remotePath);

			String zipName = FileUtil.parseFileName(remotePath);
			Path local = new Path(tempDirectory.toAbsolutePath().toString(), zipName);

			LOG.info("Copying from remote path: {} to local path: {}", remote.toString(), local.toString());
			FileSystem fs = remote.getFileSystem(new Configuration());
			fs.copyToLocalFile(remote, local);

			LOG.info("Unzipping {} to {}", local.toString(), tempDirectory.toAbsolutePath().toString());
			Preconditions.checkState(ShellExec.run(
					String.format("unzip -q -d %s %s", tempDirectory.toAbsolutePath().toString(), local.toString()), LOG::info),
					"Failed to unzip file:" + local.toString());

			// dir name is the name of the zip file without extension by default
			if (null == unzipDirName || unzipDirName.isEmpty()) {
				unzipDirName = FileUtil.getFileNameWithoutExtension(zipName);
				LOG.warn("Name of the unzip directory is not given. Set it to the name of the zip file: " + unzipDirName);
			}

			File targetDir = new File(workDir + "/" + unzipDirName);
			File tmpFile = new File(tempDirectory.toFile(), unzipDirName);
			if (!tmpFile.exists()) {
				throw new MLException(tmpFile.getAbsolutePath() + " does not exist.");
			}

			LOG.info("Renaming {} to {}", tmpFile.getAbsolutePath(), targetDir.getAbsolutePath());
			Preconditions.checkState(tmpFile.renameTo(targetDir), "Failed to rename "
					+ tmpFile.getAbsolutePath() + " to " + targetDir.getAbsolutePath());
			LOG.info("Downloaded remote file: " + remote.toString() + " to " + targetDir.getAbsolutePath());
		} finally {
			FileUtils.deleteDirectory(tempDirectory.toFile());
		}
	}
}
