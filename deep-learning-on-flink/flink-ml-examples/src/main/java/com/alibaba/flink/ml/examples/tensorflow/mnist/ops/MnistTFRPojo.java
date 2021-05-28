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

package com.alibaba.flink.ml.examples.tensorflow.mnist.ops;

import com.google.protobuf.InvalidProtocolBufferException;
import org.tensorflow.proto.example.Example;

import java.nio.charset.StandardCharsets;
import java.util.List;

public class MnistTFRPojo {

	public String image_raw;
	public int label;

	public String getImage_raw() {
		return image_raw;
	}

	public void setImage_raw(String image_raw) {
		this.image_raw = image_raw;
	}

	public int getLabel() {
		return label;
	}

	public void setLabel(int label) {
		this.label = label;
	}

	public static MnistTFRPojo from(byte[] bytes) throws InvalidProtocolBufferException {
		Example example = Example.parseFrom(bytes);
		String image = example.getFeatures().getFeatureMap().get("image_raw").getBytesList().getValue(0)
				.toString(StandardCharsets.ISO_8859_1);
		List<Long> label = example.getFeatures().getFeatureMap().get("label").getInt64List().getValueList();
		for (int i = 0; i < label.size(); i++) {
			if (label.get(i) == 1) {
				MnistTFRPojo res = new MnistTFRPojo();
				res.setImage_raw(image);
				res.setLabel(i);
				return res;
			}
		}
		throw new RuntimeException("Invalid label: " + label);
	}
}
