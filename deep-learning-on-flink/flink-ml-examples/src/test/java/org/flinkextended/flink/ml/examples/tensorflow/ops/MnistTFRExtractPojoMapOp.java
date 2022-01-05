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

package org.flinkextended.flink.ml.examples.tensorflow.ops;

import org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.MnistTFRPojo;

import org.apache.flink.api.common.functions.RichFlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.api.java.typeutils.TypeExtractor;
import org.apache.flink.util.Collector;

public class MnistTFRExtractPojoMapOp extends RichFlatMapFunction<byte[], MnistTFRPojo>
		implements ResultTypeQueryable<MnistTFRPojo> {
	@Override
	public void flatMap(byte[] value, Collector<MnistTFRPojo> out) throws Exception {
		if (value == null) {
			// TODO: how to avoid this
			return;
		}
		out.collect(MnistTFRPojo.from(value));
	}

	@Override
	public TypeInformation<MnistTFRPojo> getProducedType() {
		return TypeExtractor.getForClass(MnistTFRPojo.class);
	}
}
