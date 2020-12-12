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
package com.apache.flink.ai.flow.component;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.table.catalog.hive.HiveCatalog;
import com.apache.flink.ai.flow.ComponentContext;
import com.apache.flink.ai.flow.node.BaseNode;
import com.apache.flink.ai.flow.node.ExampleNode;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import static com.apache.flink.ai.flow.ConstantConfig.DDL_STRING;
import static com.apache.flink.ai.flow.ConstantConfig.TABLE_NAME;

public class ExampleComponent implements Component{

	@Override
	public List<Table> translate(ComponentContext context, BaseNode node, List<Table> inputs) throws Exception {
		ExampleNode exampleNode = (ExampleNode) node;
		TableEnvironment tEnv = context.getTableEnv();
		StatementSet statementSet = context.getStatementSet();
		Map<String, String> args;
		if(context.isStream()){
			args = exampleNode.getStreamArgs();
		}else {
			args = exampleNode.getBatchArgs();
		}
		if(exampleNode.isSource()){
			List<Table> resultList = new ArrayList<>();
			if(exampleNode.isCatalog()){
				String catalogName = exampleNode.getCatalogName();
				String catalogDataBase = exampleNode.getCatalogDataBase();
				catalogDataBase = catalogDataBase == null ? "default" : catalogDataBase;
				String catalogConnectionUri = exampleNode.getCatalogConnectionUri();
				String catalogVersion = exampleNode.getCatalogVersion();
				String catalogType = exampleNode.getCatalogType();
				String catalogTable = exampleNode.getCatalogTable();
				if(catalogType.equalsIgnoreCase("hive")){
					HiveCatalog hiveCatalog = new HiveCatalog(catalogName,catalogDataBase,catalogConnectionUri,catalogVersion);
					tEnv.registerCatalog(catalogName, hiveCatalog);
					tEnv.useCatalog(catalogName);
					Table table = tEnv.from(String.format("%s.%s.%s", catalogName, catalogDataBase, catalogTable));
					resultList.add(table);
				}
				else {
					throw new Exception(String.format("flink ai flow does not support %s catalog now", catalogType));
				}
			}
			else {
				String ddl = args.get(DDL_STRING);
				String tableName = args.get(TABLE_NAME);
				TableResult result = tEnv.executeSql(ddl);
				Table table = tEnv.from(tableName);
				resultList.add(table);
			}
			return resultList;
		}else {
			String ddl = args.get(DDL_STRING);
			String tableName = args.get(TABLE_NAME);
			TableResult result = tEnv.executeSql(ddl);
			statementSet.addInsert(tableName, inputs.get(0));
			return null;
		}
	}
}
