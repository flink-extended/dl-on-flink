/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.util.MLConstants;

/** Constant for Tensorflow on Flink. */
public class TFConstants {
    public static final String TF_PORT = MLConstants.SYS_PREFIX + "tf_port";
    // path of the saved model used during inference
    public static final String TF_INFERENCE_EXPORT_PATH = "tf.inference.export.path";
    // a comma separated list containing the input tensors needed for inference
    public static final String TF_INFERENCE_INPUT_TENSOR_NAMES = "tf.inference.input.tensor.names";
    // a comma separated list containing the output tensors produced by inference
    public static final String TF_INFERENCE_OUTPUT_TENSOR_NAMES =
            "tf.inference.output.tensor.names";
    /**
     * A comma separated list containing names of the fields that are needed to produce the output
     * row. The names are searched in {@link #TF_INFERENCE_OUTPUT_TENSOR_NAMES} and input
     * TableSchema. The first matching field is added to the output row.
     */
    public static final String TF_INFERENCE_OUTPUT_ROW_FIELDS = "tf.inference.output.row.fields";
    // batch size used for java inference
    public static final String TF_INFERENCE_BATCH_SIZE = "tf.inference.batch.size";

    /** make worker 0 as a flink vertex. */
    public static final String TF_IS_CHIEF_ALONE = "tf_is_chief_alone";

    public static final String TF_IS_CHIEF_ROLE = "tf_is_chief_role";
    public static final String TF_IS_WORKER_ZERO_CHIEF = "tf_is_worker_zero_chief";

    public static final String TENSORBOARD_PORT = "tensorboard_port";
    public static final String INPUT_TF_EXAMPLE_CONFIG =
            MLConstants.SYS_PREFIX + "input_tf_example_config";
    public static final String OUTPUT_TF_EXAMPLE_CONFIG =
            MLConstants.SYS_PREFIX + "output_tf_example_config";
}
