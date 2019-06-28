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

package com.alibaba.flink.ml.examples.util;

import com.alibaba.flink.ml.util.MiniCluster;
import com.alibaba.flink.ml.util.ShellExec;
import com.alibaba.flink.ml.util.TestUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;

public class CodeUtil {

	private static final Logger LOG = LoggerFactory.getLogger(CodeUtil.class);

	private static String rootPath = TestUtil.getProjectRootPath() + "/flink-ml-examples/";
	private static String sourcePath = rootPath + "src/test/python/*";
	private static String targetPath = rootPath + "target/code";

	public static String zipPythonFile() throws IOException {
		File codeZip = new File(rootPath + "/target/code.zip");
		codeZip.delete();
		if (!codeZip.exists()) {
			File codePath = new File(targetPath);
			codePath.delete();
			if (!codePath.exists()) {
				if (!codePath.mkdirs()) {
					String errMsg = "create code dir failed!";
					throwException(errMsg);
				} else {
					if (!ShellExec.run(String.format("cp %s %s", sourcePath, targetPath), LOG::info)) {
						String errMsg = "copy source code failed!";
						throwException(errMsg);
					}
				}
			}
			if (!ShellExec.run(String.format("cd %s && zip -r %s %s", rootPath + "target/",
					codeZip.getAbsolutePath(), "code"), LOG::info)) {
				String errMsg = "zip source code failed!";
				throwException(errMsg);
			}
		}
		return codeZip.getAbsolutePath();
	}

	public static String copyCodeToHdfs(MiniCluster miniCluster) throws IOException {
		String codeZipPath = zipPythonFile();
		String remoteCodePath = String.format("%s/user/root/", miniCluster.getHDFS());
		boolean res = miniCluster.copyFromHostToHDFS(codeZipPath, remoteCodePath);
		if (res) {
			return remoteCodePath + "code.zip";
		} else {
			throwException("copy code zip to hdfs failed!");
			return null;
		}
	}

	protected static void throwException(String errMsg) throws IOException {
		System.err.println(errMsg);
		throw new IOException(errMsg);
	}
}
