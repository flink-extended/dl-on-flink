/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.apache.flink.ai.flow.common;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class FileUtils {

	public static boolean exist(File file){
		return file.exists();
	}

	public static boolean deleteDir(File dir) {
		if (dir.isDirectory()) {
			String[] children = dir.list();
			for (int i = 0; i < children.length; i++) {
				boolean success = deleteDir(new File(dir, children[i]));
				if (!success) {
					return false;
				}
			}
		}
		return dir.delete();
	}

	public static String readResourceFile(String file) throws IOException {
		String fileName = FileUtils.class.getClassLoader().getResource(file).getPath();
		return readFile(fileName);
	}

	public static String readFile(String fileName) throws IOException {
		File f = new File(fileName);
		FileInputStream in = new FileInputStream(f);
		int size = in.available();
		byte[] buffer = new byte[size];
		in.read(buffer);
		in.close();
		return new String(buffer, "utf-8");
	}
}
