package com.alibaba.flink.ml.lib.tensorflow;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.scala.typeutils.Types;
import org.apache.flink.table.functions.FunctionContext;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

import com.alibaba.flink.ml.lib.tensorflow.utils.TypeMapping;
import com.google.common.base.Preconditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.tensorflow.framework.DataType;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class TFPredictUDTF extends TableFunction<Row> {
	private static Logger LOG = LoggerFactory.getLogger(TFPredictUDTF.class);
	private final String modelDir;
	private final String[] inputNames;
	private final String[] inputTypes;
	private final String[] outputNames;
	private final String[] outputTypes;
	private Map<String, String> props;
	private transient TFPredict tfPredict;
	private final int batchSize;
	private transient BlockingQueue<Object[]> rowCache;
	private ExecutorService predictService;
	private volatile boolean runningFlag = true;
	private transient Future predictFuture;

	public TFPredictUDTF(String modelDir, String[] inputNames,String[] inputTypes, String[] outputNames, String[] outputTypes,
			Map<String, String> props, int batchSize) {
		this.modelDir = modelDir;
		this.inputNames = inputNames;
		this.inputTypes = inputTypes;
		this.outputNames = outputNames;
		this.outputTypes = outputTypes;
		this.props = props;
		this.batchSize = batchSize;
	}

	private class PredictRunner implements Runnable{
		private List<Object[]> result = new ArrayList<>(batchSize);
		private int[] dimCounts = TypeMapping.getDimsByDataTypes(inputTypes);
		@Override
		public void run() {
			while (runningFlag){
				if(rowCache.isEmpty()){
					try {
						Object[] objects = rowCache.poll(1, TimeUnit.SECONDS);
						if(null == objects){
							continue;
						}else {
							result.add(objects);
						}
					} catch (InterruptedException e) {
						e.printStackTrace();
						runningFlag = false;
					}
				}else {
					int size = rowCache.drainTo(result);
				}
				Row[] rows = tfPredict.predict(result, dimCounts);
				for(Row r: rows){
					collect(r);
				}
				result.clear();
			}
			if(!rowCache.isEmpty()){
				int size = rowCache.drainTo(result);
				Row[] rows = tfPredict.predict(result, dimCounts);
				for(Row r: rows){
					collect(r);
				}
				result.clear();
			}
		}
	}

	@Override
	public void open(FunctionContext context) throws Exception {
		super.open(context);
		rowCache = new LinkedBlockingQueue<>(this.batchSize);
		DataType[] inputTypes = TypeMapping.convertToDataTypes(this.inputTypes);
		tfPredict = new TFPredict(modelDir, props, inputNames, inputTypes, outputNames, outputTypes);
		predictService = Executors.newFixedThreadPool(1, r->{
			Thread t = new Thread(r);
			t.setDaemon(true);
			t.setName("predict-thread");
			return t;
		});
		predictFuture = predictService.submit(new PredictRunner());
	}

	@Override
	public void close() throws Exception {
		super.close();
		runningFlag = false;
		if(null != predictFuture){
			predictFuture.get();
		}
		if(null != predictService){
			predictService.shutdown();
			predictService.awaitTermination(5, TimeUnit.SECONDS);
		}
		if(null != tfPredict){
			tfPredict.close();
		}
	}



	@Override
	public TypeInformation<Row> getResultType() {
		return Types.ROW(outputNames, TypeMapping.convertToTypeInformation(outputTypes));
	}

	public void eval(Object... objects) {
		Preconditions.checkArgument(objects.length == inputNames.length,
				"Input fields length mismatch");
		try {
			rowCache.put(objects);
		} catch (InterruptedException e) {
			e.printStackTrace();
			throw new RuntimeException(e.getMessage());
		}
	}
}
