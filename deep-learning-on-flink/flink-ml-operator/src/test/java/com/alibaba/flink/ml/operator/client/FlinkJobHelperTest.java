package com.alibaba.flink.ml.operator.client;

import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.PrintSinkFunction;
import org.apache.flink.streaming.api.graph.StreamGraph;
import org.apache.flink.streaming.api.graph.StreamNode;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class FlinkJobHelperTest {

	private StreamGraph streamGraph;

	@Before
	public void setUp() throws Exception {
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.fromElements(1, 2, 3)
				.map((MapFunction<Integer, Integer>) integer -> integer + 1).name("map")
				.addSink(new PrintSinkFunction<>());
		streamGraph = env.getStreamGraph();
	}

	@Test
	public void streamPlan() {
		assertEquals(streamGraph.getStreamingPlanAsJSON(), FlinkJobHelper.streamPlan(streamGraph));
	}

	@Test
	public void like() {
		final FlinkJobHelper flinkJobHelper = new FlinkJobHelper();
		flinkJobHelper.like("map", 3);
		flinkJobHelper.matchStreamGraph(streamGraph);

		boolean nodeExist = false;
		for (StreamNode streamNode : streamGraph.getStreamNodes()) {
			if (streamNode.getOperatorName().equals("map")) {
				nodeExist = true;
				assertEquals(3, streamNode.getParallelism());
			}
		}
		assertTrue(nodeExist);
	}

	@Test
	public void setDefaultParallelism() {
		final FlinkJobHelper flinkJobHelper = new FlinkJobHelper();
		flinkJobHelper.setDefaultParallelism(5);
		flinkJobHelper.matchStreamGraph(streamGraph);
		for (StreamNode streamNode : streamGraph.getStreamNodes()) {
			assertEquals(5, streamNode.getParallelism());
		}
	}
}