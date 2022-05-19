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

package org.flinkextended.flink.ml.tensorflow.coding;

/** Dummy class for unit test. */
public class MyPojo {
    public String f0;
    public Long f1;

    public String getF0() {
        return f0;
    }

    public void setF0(String f0) {
        this.f0 = f0;
    }

    public Long getF1() {
        return f1;
    }

    public void setF1(Long f1) {
        this.f1 = f1;
    }
}
