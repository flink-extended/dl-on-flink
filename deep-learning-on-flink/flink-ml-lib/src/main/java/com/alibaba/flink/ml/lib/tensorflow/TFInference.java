package com.alibaba.flink.ml.lib.tensorflow;

import org.apache.commons.lang.ArrayUtils;
import org.apache.flink.types.Row;

import com.alibaba.flink.ml.lib.tensorflow.utils.TensorConversion;
import com.google.common.base.Preconditions;
import com.google.common.io.Files;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.tensorflow.SavedModelBundle;
import org.tensorflow.Session;
import org.tensorflow.Tensor;
import org.tensorflow.proto.framework.ConfigProto;
import org.tensorflow.proto.framework.DataType;
import org.tensorflow.proto.framework.MetaGraphDef;
import org.tensorflow.proto.framework.SignatureDef;
import org.tensorflow.proto.framework.TensorInfo;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

/**
 * TFPredict load tensorflow saved model do inference.
 */
public class TFInference {
	private static Logger LOG = LoggerFactory.getLogger(TFInference.class);
	private static final String TAG = "serve";

	private final String[] inputNames;
	private final DataType[] inputDataTypes;
	private final int[] inputRanks;
	private final String[] inputTensorNames;
	private final String[] outputNames;
	private DataType[] outputDataTypes;
	private final int[] outputRanks;
	private final String[] outputTensorNames;
	private Properties properties;
	private Map<String, Integer> inputNameToRank = new HashMap<>();
	private final SavedModelBundle model;
	private final SignatureDef modelSig;
	private final Set<String> inputTensorNameSet;
	private File downloadModelPath;

	/***
	 * TFPredict constructor
	 * @param modelDir saved model dir
	 * @param properties some properties
	 * @param inputNames input field names
	 * @param inputDataTypes input DataType
	 * @param outputNames output field names
	 * @param outputDataTypes output TypeDef
	 * @throws Exception
	 */
	public TFInference(String modelDir,
			String[] inputNames,
			DataType[] inputDataTypes,
			int[] inputRanks,
			String[] outputNames,
			DataType[] outputDataTypes,
			int[] outputRanks,
			Properties properties)
			throws Exception {
		this.inputNames = inputNames;
		this.inputDataTypes = inputDataTypes;
		this.inputRanks = inputRanks;
		this.outputNames = outputNames;
		this.outputDataTypes = outputDataTypes;
		this.outputRanks = outputRanks;
		this.properties = properties;
		for(int i = 0; i < inputRanks.length; i++){
			this.inputRanks[i]++;
		}
		for(int i = 0; i < outputRanks.length; i++){
			this.outputRanks[i]++;
		}

		for(int i = 0; i < inputNames.length; i++){
			inputNameToRank.put(this.inputNames[i], this.inputRanks[i]);
		}

		// load model
		Path modelPath = new Path(modelDir);
		String scheme = modelPath.toUri().getScheme();
		ConfigProto configProto = ConfigProto.newBuilder()
				.setAllowSoftPlacement(true) // allow less GPUs than configured
				.build();
		// local fs is assumed when no scheme provided
		if (StringUtils.isEmpty(scheme) || scheme.equals("file")) {
			model = SavedModelBundle.loader(modelDir)
					.withConfigProto(configProto)
					.withTags(TAG)
					.load();
		} else if (scheme.equals("hdfs")) {
			// download the model from hdfs
			FileSystem fs = modelPath.getFileSystem(new Configuration());
			downloadModelPath = Files.createTempDir();
			Path localPath = new Path(downloadModelPath.getPath(), modelPath.getName());
			LOG.info("Downloading model from {} to {}", modelPath, localPath);
			fs.copyToLocalFile(modelPath, localPath);
			//model = SavedModelBundle.load(localPath.toString(), TAG);
			model = SavedModelBundle.loader(localPath.toString())
					.withConfigProto(configProto)
					.withTags(TAG)
					.load();
		} else {
			throw new IllegalArgumentException("Model URI not supported: " + modelDir);
		}
		modelSig = MetaGraphDef.parseFrom(model.metaGraphDef().toByteArray()).getSignatureDefOrThrow("serving_default");
		logSignature();
		inputTensorNameSet = modelSig.getInputsMap().keySet();
		inputTensorNames = inputTensorNameSet.toArray(new String[0]);
		Set<String> inputNamesSet = new HashSet<>(Arrays.asList(inputNames));
		// input tensor names must exist in the input fields
		Preconditions.checkArgument(inputNamesSet.containsAll(inputTensorNameSet),
				"Invalid input tensor names: " + Arrays.toString(inputTensorNames));

		Set<String> outputTensorNameSet = modelSig.getOutputsMap().keySet();
		outputTensorNames = outputTensorNameSet.toArray(new String[0]);
		// output tensor names must exist in the model
		Preconditions.checkArgument(modelSig.getOutputsMap().keySet().containsAll(Arrays.asList(outputTensorNames)),
				"Invalid output tensor names: " + Arrays.toString(outputTensorNames));

	}

	/**
	 * do tensorflow inference
	 * @param batchRecord input rows
	 * @return inference rows
	 */
	public Row[] inference(List<Object[]> batchRecord) {
		if(batchRecord.isEmpty()){
			return null;
		}else {
			Session.Runner runner = model.session().runner();
			int size = batchRecord.size();
			Row[] rows = new Row[batchRecord.size()];
			Map<String, Object> inNameToObjs = new HashMap<>(inputNames.length);
			for (int i = 0; i < inputNames.length; i++) {
				inNameToObjs.put(inputNames[i], extractCols(batchRecord, i, size, inputRanks[i], inputDataTypes[i]));
			}
			List<Tensor<?>> toClose = new ArrayList<>(inputTensorNameSet.size() + outputTensorNames.length);
			try {
				for (int i = 0; i < inputTensorNames.length; i++) {
					TensorInfo inputInfo = modelSig.getInputsMap().get(inputTensorNames[i]);
					Tensor<?> tensor = TensorConversion.toTensor(inNameToObjs.get(inputTensorNames[i]),
							inputInfo, inputNameToRank.get(inputTensorNames[i]));
					toClose.add(tensor);
					runner.feed(inputInfo.getName(), tensor);
				}
				for (String outputTensorName : outputTensorNames) {
					TensorInfo outputInfo = modelSig.getOutputsMap().get(outputTensorName);
					runner.fetch(outputInfo.getName());
				}
				List<Tensor<?>> outTensors = runner.run();
				toClose.addAll(outTensors);
				Map<String, Tensor<?>> outNameToTensor = new HashMap<>();
				for (int i = 0; i < outputTensorNames.length; i++) {
					outNameToTensor.put(outputTensorNames[i], outTensors.get(i));
				}
				for (int i = 0; i < outputNames.length; i++) {
					Object cols;
					if (outNameToTensor.containsKey(outputNames[i])) {
						cols = TensorConversion.fromTensor(outNameToTensor.get(outputNames[i]));
					} else {
						cols = inNameToObjs.get(outputNames[i]);
					}
					for (int j = 0; j < rows.length; j++) {
						if (rows[j] == null) {
							rows[j] = new Row(outputNames.length);
						}
						setRowField(rows[j], i, cols, j, outputRanks[i], this.outputDataTypes[i]);
						//rows[j].setField(i, cols[j]);
					}
				}
			} catch (Exception e) {
				LOG.error("Error in inference: ", e);
			} finally {
				for (Tensor<?> tensor : toClose) {
					tensor.close();
				}
				toClose.clear();
			}
			return rows;
		}
	}
	private void setRowField(Row row, int index, Object object, int col, int rank, DataType dataType){
		switch (dataType){
			case DT_INT32: {
				switch (rank){
					case 1:{
						int[] value = (int[])object;
						row.setField(index, value[col]);
						return;
					}
					case 2:{
						int[][] value = (int[][])object;
						row.setField(index, value[col]);
						return;
					}
					case 3:{
						int[][][] value = (int[][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 4:{
						int[][][][] value = (int[][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 5:{
						int[][][][][] value = (int[][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 6:{
						int[][][][][][] value = (int[][][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_INT64: {
				switch (rank){
					case 1:{
						long[] value = (long[])object;
						row.setField(index, value[col]);
						return;
					}
					case 2:{
						long[][] value = (long[][])object;
						row.setField(index, value[col]);
						return;
					}
					case 3:{
						long[][][] value = (long[][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 4:{
						long[][][][] value = (long[][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 5:{
						long[][][][][] value = (long[][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 6:{
						long[][][][][][] value = (long[][][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_FLOAT: {
				switch (rank){
					case 1:{
						float[] value = (float[])object;
						row.setField(index, value[col]);
						return;
					}
					case 2:{
						float[][] value = (float[][])object;
						row.setField(index, value[col]);
						return;
					}
					case 3:{
						float[][][] value = (float[][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 4:{
						float[][][][] value = (float[][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 5:{
						float[][][][][] value = (float[][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 6:{
						float[][][][][][] value = (float[][][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_DOUBLE: {
				switch (rank){
					case 1:{
						double[] value = (double[])object;
						row.setField(index, value[col]);
						return;
					}
					case 2:{
						double[][] value = (double[][])object;
						row.setField(index, value[col]);
						return;
					}
					case 3:{
						double[][][] value = (double[][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 4:{
						double[][][][] value = (double[][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 5:{
						double[][][][][] value = (double[][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 6:{
						double[][][][][][] value = (double[][][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_STRING: {
				switch (rank){
					case 1:{
						String[] value = (String[])object;
						row.setField(index, value[col]);
						return;
					}
					case 2:{
						String[][] value = (String[][])object;
						row.setField(index, value[col]);
						return;
					}
					case 3:{
						String[][][] value = (String[][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 4:{
						String[][][][] value = (String[][][][])object;
						row.setField(index, value[col]);
						return;
					}
					case 5:{
						String[][][][][] value = (String[][][][][])object;
						row.setField(index, value[col]);
						return;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			default:
				throw new UnsupportedOperationException(
						"Type can't be converted to tensor: " + dataType.name());
		}
	}
	public void close() throws IOException {
		if (model != null) {
			model.close();
			LOG.info("Model closed");
		}
		if (downloadModelPath != null) {
			FileUtils.deleteQuietly(downloadModelPath);
		}
	}

	private void logSignature() {
		int numInputs = modelSig.getInputsCount();
		StringBuilder builder = new StringBuilder();
		int i = 1;
		builder.append("\n----MODEL SIGNATURE--------------------------\n");
		builder.append("Inputs:\n");
		for (Map.Entry<String, TensorInfo> entry : modelSig.getInputsMap().entrySet()) {
			TensorInfo t = entry.getValue();
			builder.append(String.format(
					"%d of %d: %-20s (Node name in graph: %-20s, type: %s)\n",
					i++, numInputs, entry.getKey(), t.getName(), t.getDtype()));
		}
		int numOutputs = modelSig.getOutputsCount();
		i = 1;
		builder.append("Outputs:\n");
		for (Map.Entry<String, TensorInfo> entry : modelSig.getOutputsMap().entrySet()) {
			TensorInfo t = entry.getValue();
			builder.append(String.format(
					"%d of %d: %-20s (Node name in graph: %-20s, type: %s)\n",
					i++, numOutputs, entry.getKey(), t.getName(), t.getDtype()));
		}
		builder.append("-------------------------------------------------");
		System.out.println(builder.toString());
	}

	private Object extractCols(List<Object[]> cache, int index, int len, int rank, DataType dataType) {
		switch (dataType){
			case DT_INT32: {
				switch (rank){
					case 1:{
						int[] res = new int[len];
						for (int i = 0; i < res.length; i++) {
							res[i] = (int)cache.get(i)[index];
						}
						return res;
					}
					case 2:{
						int[][] res = new int[len][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Integer[]) cache.get(i)[index]);
						}
						return res;
					}
					case 3:{
						int[][][] res = new int[len][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Integer[][]) cache.get(i)[index]);
						}
						return res;
					}
					case 4:{
						int[][][][] res = new int[len][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Integer[][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 5:{
						int[][][][][] res = new int[len][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Integer[][][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 6:{
						int[][][][][][] res = new int[len][][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Integer[][][][][]) cache.get(i)[index]);
						}
						return res;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_INT64: {
				switch (rank){
					case 1:{
						long[] res = new long[len];
						for (int i = 0; i < res.length; i++) {
							res[i] = (long)cache.get(i)[index];
						}
						return res;
					}
					case 2:{
						long[][] res = new long[len][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Long[]) cache.get(i)[index]);
						}
						return res;
					}
					case 3:{
						long[][][] res = new long[len][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Long[][]) cache.get(i)[index]);
						}
						return res;
					}
					case 4:{
						long[][][][] res = new long[len][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Long[][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 5:{
						long[][][][][] res = new long[len][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Long[][][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 6:{
						long[][][][][][] res = new long[len][][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Long[][][][][]) cache.get(i)[index]);
						}
						return res;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_FLOAT: {
				switch (rank){
					case 1:{
						float[] res = new float[len];
						for (int i = 0; i < res.length; i++) {
							res[i] = (float)cache.get(i)[index];
						}
						return res;
					}
					case 2:{
						float[][] res = new float[len][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Float[]) cache.get(i)[index]);
						}
						return res;
					}
					case 3:{
						float[][][] res = new float[len][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Float[][]) cache.get(i)[index]);
						}
						return res;
					}
					case 4:{
						float[][][][] res = new float[len][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Float[][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 5:{
						float[][][][][] res = new float[len][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Float[][][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 6:{
						float[][][][][][] res = new float[len][][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Float[][][][][]) cache.get(i)[index]);
						}
						return res;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_DOUBLE: {
				switch (rank){
					case 1:{
						double[] res = new double[len];
						for (int i = 0; i < res.length; i++) {
							res[i] = (double)cache.get(i)[index];
						}
						return res;
					}
					case 2:{
						double[][] res = new double[len][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Double[]) cache.get(i)[index]);
						}
						return res;
					}
					case 3:{
						double[][][] res = new double[len][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Double[][]) cache.get(i)[index]);
						}
						return res;
					}
					case 4:{
						double[][][][] res = new double[len][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Double[][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 5:{
						double[][][][][] res = new double[len][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Double[][][][]) cache.get(i)[index]);
						}
						return res;
					}
					case 6:{
						double[][][][][][] res = new double[len][][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = toPrimitive((Double[][][][][]) cache.get(i)[index]);
						}
						return res;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			case DT_STRING: {
				switch (rank){
					case 1:{
						String[] res = new String[len];
						for (int i = 0; i < res.length; i++) {
							res[i] = (String)cache.get(i)[index];
						}
						return res;
					}
					case 2:{
						String[][] res = new String[len][];
						for (int i = 0; i < res.length; i++) {
							res[i] = (String[])cache.get(i)[index];
						}
						return res;
					}
					case 3:{
						String[][][] res = new String[len][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = (String[][])cache.get(i)[index];
						}
						return res;
					}
					case 4:{
						String[][][][] res = new String[len][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = (String[][][])cache.get(i)[index];
						}
						return res;
					}
					case 5:{
						String[][][][][] res = new String[len][][][][];
						for (int i = 0; i < res.length; i++) {
							res[i] = (String[][][][])cache.get(i)[index];
						}
						return res;
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(rank));
				}
			}
			default:
				throw new UnsupportedOperationException(
						"Type can't be converted to tensor: " + dataType.name());
		}
	}

	// helper functions to convert the nd-array of Object to primitives
	private float[] toPrimitive(Float[] floats) {
		return ArrayUtils.toPrimitive(floats);
	}

	private float[][] toPrimitive(Float[][] floats) {
		return Arrays.stream(floats).map(this::toPrimitive).toArray(float[][]::new);
	}

	private float[][][] toPrimitive(Float[][][] floats) {
		return Arrays.stream(floats).map(this::toPrimitive).toArray(float[][][]::new);
	}

	private float[][][][] toPrimitive(Float[][][][] floats) {
		return Arrays.stream(floats).map(this::toPrimitive).toArray(float[][][][]::new);
	}

	private float[][][][][] toPrimitive(Float[][][][][] floats) {
		return Arrays.stream(floats).map(this::toPrimitive).toArray(float[][][][][]::new);
	}

	private double[] toPrimitive(Double[] doubles) {
		return ArrayUtils.toPrimitive(doubles);
	}

	private double[][] toPrimitive(Double[][] doubles) {
		return Arrays.stream(doubles).map(this::toPrimitive).toArray(double[][]::new);
	}

	private double[][][] toPrimitive(Double[][][] doubles) {
		return Arrays.stream(doubles).map(this::toPrimitive).toArray(double[][][]::new);
	}

	private double[][][][] toPrimitive(Double[][][][] doubles) {
		return Arrays.stream(doubles).map(this::toPrimitive).toArray(double[][][][]::new);
	}

	private double[][][][][] toPrimitive(Double[][][][][] doubles) {
		return Arrays.stream(doubles).map(this::toPrimitive).toArray(double[][][][][]::new);
	}

	private int[] toPrimitive(Integer[] ints) {
		return ArrayUtils.toPrimitive(ints);
	}

	private int[][] toPrimitive(Integer[][] ints) {
		return Arrays.stream(ints).map(this::toPrimitive).toArray(int[][]::new);
	}

	private int[][][] toPrimitive(Integer[][][] ints) {
		return Arrays.stream(ints).map(this::toPrimitive).toArray(int[][][]::new);
	}

	private int[][][][] toPrimitive(Integer[][][][] ints) {
		return Arrays.stream(ints).map(this::toPrimitive).toArray(int[][][][]::new);
	}

	private int[][][][][] toPrimitive(Integer[][][][][] ints) {
		return Arrays.stream(ints).map(this::toPrimitive).toArray(int[][][][][]::new);
	}

	private long[] toPrimitive(Long[] longs) {
		return ArrayUtils.toPrimitive(longs);
	}

	private long[][] toPrimitive(Long[][] longs) {
		return Arrays.stream(longs).map(this::toPrimitive).toArray(long[][]::new);
	}

	private long[][][] toPrimitive(Long[][][] longs) {
		return Arrays.stream(longs).map(this::toPrimitive).toArray(long[][][]::new);
	}

	private long[][][][] toPrimitive(Long[][][][] longs) {
		return Arrays.stream(longs).map(this::toPrimitive).toArray(long[][][][]::new);
	}

	private long[][][][][] toPrimitive(Long[][][][][] longs) {
		return Arrays.stream(longs).map(this::toPrimitive).toArray(long[][][][][]::new);
	}

}
