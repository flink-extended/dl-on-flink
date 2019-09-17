package com.alibaba.flink.ml.workflow.common;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class FileUtils {

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
