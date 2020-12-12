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

import org.apache.flink.api.common.io.FileOutputFormat;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.DataSet;
import org.apache.flink.api.java.operators.DataSink;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSink;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.sinks.AppendStreamTableSink;
import org.apache.flink.table.sinks.BatchTableSink;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.types.Row;
import java.io.IOException;
import java.io.Serializable;

public class PrintTableSink implements BatchTableSink<Row>, AppendStreamTableSink<Row>, Serializable {
	private String[] fieldNames;
	private TypeInformation<?>[] fieldTypes;


	@Override
	public TypeInformation<Row> getOutputType() {
		return new RowTypeInfo(this.fieldTypes, this.fieldNames);
	}

	@Override
	public TableSchema getTableSchema() {
		return new TableSchema(this.fieldNames, this.fieldTypes);
	}

	@Override
	public TableSink<Row> configure(String[] fieldNames, TypeInformation<?>[] fieldTypes) {
		this.fieldNames = fieldNames;
		this.fieldTypes = fieldTypes;
		return this;
	}

	@Override
	public DataSink<?> consumeDataSet(DataSet<Row> dataSet) {
		return dataSet.write(new FileOutputFormat<Row>() {
			@Override
			public void writeRecord(Row record) throws IOException {
				System.out.println(record);
			}
		}, "/tmp/print");
	}

	@Override
	public DataStreamSink<?> consumeDataStream(DataStream<Row> dataStream) {
		return dataStream.addSink(new SinkFunction<Row>() {
			@Override
			public void invoke(Row value, Context context) throws Exception {
				System.out.println(value);
			}
		});
	}
}
