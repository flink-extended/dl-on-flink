package com.alibaba.flink.ml.workflow.components.examples.csv;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.sinks.CsvTableSink;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.table.sources.CsvTableSource;
import org.apache.flink.table.sources.TableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.common.DataTypeUtils;
import com.alibaba.flink.ml.workflow.components.examples.ExampleCreator;

public class CSVExampleCreator implements ExampleCreator {
	@Override
	public TableSource createSource(ExampleProto exampleProto) throws Exception {
		CsvTableSource.Builder csvTable = CsvTableSource
				.builder()
				.path(exampleProto.getBatchUri());
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
	public TableSink createSink(ExampleProto exampleProto) throws Exception {
		CsvTableSink csvTableSink = new CsvTableSink(exampleProto.getBatchUri());
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
