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

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.util.MLConstants;

/** Constant for PyTorch on Flink. */
public class PyTorchConstants {
    public static final String PYTORCH_MASTER_IP = MLConstants.SYS_PREFIX + "pytorch_master_ip";
    public static final String PYTORCH_MASTER_PORT = MLConstants.SYS_PREFIX + "pytorch_master_port";
}
