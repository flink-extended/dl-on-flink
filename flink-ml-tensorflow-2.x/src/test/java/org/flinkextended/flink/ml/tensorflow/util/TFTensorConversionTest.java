package org.flinkextended.flink.ml.tensorflow.util;

import org.junit.Test;
import org.tensorflow.Tensor;
import org.tensorflow.ndarray.Shape;
import org.tensorflow.proto.framework.DataType;
import org.tensorflow.proto.framework.TensorInfo;
import org.tensorflow.types.TFloat32;
import org.tensorflow.types.TFloat64;
import org.tensorflow.types.TInt32;
import org.tensorflow.types.TInt64;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.*;

public class TFTensorConversionTest {
	@Test
	public void testToTensor() {

		Tensor<?> tensor = TFTensorConversion
				.toTensor(new int[][]{ new int[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_INT32).build());
		assertEquals(2, tensor.shape().numDimensions());
		assertEquals(1, tensor.shape().size(0));
		assertEquals(3, tensor.shape().size(1));

		tensor = TFTensorConversion
				.toTensor(new long[][]{ new long[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_INT64).build());
		assertEquals(2, tensor.shape().numDimensions());
		assertEquals(1, tensor.shape().size(0));
		assertEquals(3, tensor.shape().size(1));

		tensor = TFTensorConversion
				.toTensor(new float[][]{ new float[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_FLOAT).build());
		assertEquals(2, tensor.shape().numDimensions());
		assertEquals(1, tensor.shape().size(0));
		assertEquals(3, tensor.shape().size(1));

		tensor = TFTensorConversion
				.toTensor(new double[][]{ new double[] {1, 2, 3} }, TensorInfo.newBuilder().setDtype(DataType.DT_DOUBLE).build());
		assertEquals(2, tensor.shape().numDimensions());
		assertEquals(1, tensor.shape().size(0));
		assertEquals(3, tensor.shape().size(1));

	}

	@Test
	public void testFromTensor() {
		Tensor<?> tensor = TInt32.tensorOf(Shape.of(3));
		Object[] objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Integer.class));

		tensor = TFloat32.tensorOf(Shape.of(3));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Float.class));

		tensor = TInt64.tensorOf(Shape.of(3));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Long.class));

		tensor = TFloat64.tensorOf(Shape.of(3));
		objects = TFTensorConversion.fromTensor(tensor);
		assertEquals(3, objects.length);
		assertThat(objects[0], instanceOf(Double.class));
	}
}