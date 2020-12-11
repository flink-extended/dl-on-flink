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

package com.alibaba.flink.ml.examples.tensorflow.ops;

import com.alibaba.flink.ml.tensorflow.io.TFRToRowTableSource;

import java.io.File;

import static com.alibaba.flink.ml.examples.tensorflow.mnist.MnistJavaInference.CONVERTERS;
import static com.alibaba.flink.ml.examples.tensorflow.mnist.MnistJavaInference.OUT_ROW_TYPE;


public class MnistTFRToRowTableSource extends TFRToRowTableSource {

	public MnistTFRToRowTableSource(String[] paths, int epochs) {
		super(paths, epochs, OUT_ROW_TYPE, CONVERTERS);
	}

	public MnistTFRToRowTableSource(File[] files, int epochs) {
		super(files, epochs, OUT_ROW_TYPE, CONVERTERS);
	}

	public MnistTFRToRowTableSource(String[] paths, int epochs, String[] outColAliases) {
		super(paths, epochs, OUT_ROW_TYPE, outColAliases, CONVERTERS);
	}

	public MnistTFRToRowTableSource(File[] files, int epochs, String[] outColAliases) {
		super(files, epochs, OUT_ROW_TYPE, outColAliases, CONVERTERS);
	}
}
