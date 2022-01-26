package org.flinkextended.flink.ml.tensorflow.util;

import org.junit.Test;
import org.tensorflow.Tensor;
import org.tensorflow.framework.DataType;
import org.tensorflow.framework.TensorInfo;

import java.nio.DoubleBuffer;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.LongBuffer;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;

public class TFTensorConversionTest {
	@Test
	public void testToTensor() {

		Tensor<?> tensor = TFTensorConversion
				.toTensor(new int[][]{ new int[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_INT32).build());
		assertEquals(2, tensor.shape().length);
		assertEquals(1, tensor.shape()[0]);
		assertEquals(3, tensor.shape()[1]);

		tensor = TFTensorConversion
				.toTensor(new long[][]{ new long[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_INT64).build());
		assertEquals(2, tensor.shape().length);
		assertEquals(1, tensor.shape()[0]);
		assertEquals(3, tensor.shape()[1]);

		tensor = TFTensorConversion
				.toTensor(new float[][]{ new float[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_FLOAT).build());
		assertEquals(2, tensor.shape().length);
		assertEquals(1, tensor.shape()[0]);
		assertEquals(3, tensor.shape()[1]);

		tensor = TFTensorConversion
				.toTensor(new double[][]{ new double[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_DOUBLE).build());
		assertEquals(2, tensor.shape().length);
		assertEquals(1, tensor.shape()[0]);
		assertEquals(3, tensor.shape()[1]);

	}

	@Test
	public void testFromTensor() {
		Tensor<?> tensor = Tensor.create(new long[]{3}, IntBuffer.wrap(new int[]{1, 2, 3}));
		Object[] objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Integer.class));

		tensor = Tensor.create(new long[]{3}, FloatBuffer.wrap(new float[]{1, 2, 3}));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Float.class));

		tensor = Tensor.create(new long[]{3}, LongBuffer.wrap(new long[]{1, 2, 3}));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Long.class));

		tensor = Tensor.create(new long[]{3}, DoubleBuffer.wrap(new double[]{1, 2, 3}));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Double.class));
	}
}