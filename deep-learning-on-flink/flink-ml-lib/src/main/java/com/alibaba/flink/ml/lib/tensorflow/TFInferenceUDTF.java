package com.alibaba.flink.ml.lib.tensorflow;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.scala.typeutils.Types;
import org.apache.flink.table.functions.FunctionContext;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

import com.alibaba.flink.ml.lib.tensorflow.utils.RankUtil;
import com.alibaba.flink.ml.lib.tensorflow.utils.TypeMapping;
import com.google.common.base.Preconditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.tensorflow.proto.framework.DataType;

import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class TFInferenceUDTF extends TableFunction<Row> {
	private static Logger LOG = LoggerFactory.getLogger(TFInferenceUDTF.class);
	private final String modelDir;
	private final String[] inputNames;
	private final String[] inputTypes;
	private final String[] inputRanks;
	private final String[] outputNames;
	private final String[] outputTypes;
	private final String[] outputRanks;
	private Properties props;
	private transient TFInference tfInference;
	private final int batchSize;
	private transient BlockingQueue<Object[]> rowCache;
	private ExecutorService predictService;
	private volatile boolean runningFlag = true;
	private transient Future predictFuture;
	private static String SEP = ",";
	private volatile boolean failed = false;

	private String[] trim(String[] array){
		for(int i = 0; i < array.length; i++){
			array[i] = array[i].trim();
		}
		return array;
	}
	public TFInferenceUDTF(String modelDir,
			String inputNames,
			String inputTypes,
			String inputRanks,
			String outputNames,
			String outputTypes,
			String outputRanks,
			Properties props, int batchSize) {
		this.modelDir = modelDir;
		this.inputNames = inputNames.split(SEP);
		trim(this.inputNames);
		this.inputTypes = inputTypes.split(SEP);
		trim(this.inputTypes);
		this.inputRanks = inputRanks.split(SEP);
		trim(this.inputRanks);
		this.outputNames = outputNames.split(SEP);
		trim(this.outputNames);
		this.outputTypes = outputTypes.split(SEP);
		trim(this.outputTypes);
		this.outputRanks = outputRanks.split(SEP);
		trim(this.outputRanks);
		this.props = props;
		this.batchSize = batchSize;
	}

	private class PredictRunner implements Runnable{
		private List<Object[]> result = new ArrayList<>(batchSize);
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
				Row[] rows = tfInference.inference(result);
				for(Row r: rows){
					collect(r);
				}
				result.clear();
			}
			if(!rowCache.isEmpty()){
				int size = rowCache.drainTo(result);
				Row[] rows = tfInference.inference(result);
				for(Row r: rows){
					collect(r);
				}
				result.clear();
			}
		}
	}

	class InferenceExceptionHandler implements Thread.UncaughtExceptionHandler {
		@Override
		public void uncaughtException(Thread t, Throwable e) {
			e.printStackTrace();
			rowCache.clear();
			failed = true;
		}
	}
	@Override
	public void open(FunctionContext context) throws Exception {
		super.open(context);
		rowCache = new LinkedBlockingQueue<>(this.batchSize);
		DataType[] inputTypes = TypeMapping.convertToDataTypes(this.inputTypes);
		DataType[] outputTypes = TypeMapping.convertToDataTypes(this.outputTypes);
		int[] inputRanks = RankUtil.toRanks(this.inputRanks);
		int[] outputRanks = RankUtil.toRanks(this.outputRanks);

		tfInference = new TFInference(modelDir, inputNames, inputTypes, inputRanks,
				outputNames, outputTypes, outputRanks, props);
		predictService = Executors.newFixedThreadPool(1, r->{
			Thread t = new Thread(r);
			t.setDaemon(true);
			t.setName("inference-thread");
			t.setUncaughtExceptionHandler(new InferenceExceptionHandler());
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
		if(null != tfInference){
			tfInference.close();
		}
	}



	@Override
	public TypeInformation<Row> getResultType() {
		return Types.ROW(outputNames, TypeMapping.convertToTypeInformation(outputTypes,
				RankUtil.toRanks(this.outputRanks)));
	}

	public void eval(Object... objects) {
		if(failed){
			throw new RuntimeException("inference thread failed!");
		}
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
