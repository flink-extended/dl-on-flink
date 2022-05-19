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

package org.flinkextended.flink.ml.operator.ops.inputformat;

import org.apache.flink.core.io.InputSplit;

import java.util.Objects;

/** machine learning cluster corresponds to input split. */
public class NodeInputSplit implements InputSplit {
    private final int num;
    private final int index;

    public NodeInputSplit(int num, int index) {
        this.num = num;
        this.index = index;
    }

    /** @return total split number. */
    public int getTotalNumberOfSplits() {
        return num;
    }

    /** @return split index. */
    @Override
    public int getSplitNumber() {
        return index;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        NodeInputSplit that = (NodeInputSplit) o;
        return num == that.num && index == that.index;
    }

    @Override
    public int hashCode() {
        return Objects.hash(num, index);
    }
}
