package com.alibaba.flink.ml.workflow.components.examples.csv;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.sinks.CsvTableSink;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.table.sources.CsvTableSource;
import org.apache.flink.table.sources.TableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.RunModeProto;
import com.alibaba.flink.ml.workflow.common.DataTypeUtils;
import com.alibaba.flink.ml.workflow.components.examples.ExampleCreator;

public class CSVExampleCreator implements ExampleCreator {
	@Override
	public TableSource createSource(ExampleProto exampleProto, RunModeProto runMode) throws Exception {
		CsvTableSource.Builder csvTable = CsvTableSource
				.builder();
		if(RunModeProto.BATCH == runMode) {
			csvTable.path(exampleProto.getBatchUri());
		}else {
			csvTable.path(exampleProto.getStreamUri());
		}
		if(exampleProto.getMeta().getPropertiesOrDefault("skipFirstLine", "False")
				.equalsIgnoreCase("True")){
			csvTable = csvTable.ignoreFirstLine();
		}
		String fieldDelimiter = exampleProto.getMeta().getPropertiesOrDefault("fieldDelimiter", ",");
		csvTable = csvTable.fieldDelimiter(fieldDelimiter);
		for(int i = 0; i < exampleProto.getSchema().getNameListCount(); i++){
			csvTable = csvTable.field(exampleProto.getSchema().getNameList(i),
					DataTypeUtils.toTypeInformation(exampleProto.getSchema().getTypeList(i)));
		}
		return csvTable.build();
	}

	@Override
	public TableSink createSink(ExampleProto exampleProto, RunModeProto runMode) throws Exception {
		CsvTableSink csvTableSink;
		if(RunModeProto.BATCH == runMode) {
			csvTableSink = new CsvTableSink(exampleProto.getBatchUri());
		}else {
			csvTableSink = new CsvTableSink(exampleProto.getStreamUri());
		}
		int count = exampleProto.getSchema().getNameListCount();
		String[] names = new String[count];
		TypeInformation[] types = new TypeInformation[count];
		for(int i = 0; i < count; i++){
			names[i] = exampleProto.getSchema().getNameList(i);
			types[i] = DataTypeUtils.toTypeInformation(exampleProto.getSchema().getTypeList(i));
		}
		csvTableSink = (CsvTableSink)csvTableSink.configure(names, types);
		return csvTableSink;
	}
}
