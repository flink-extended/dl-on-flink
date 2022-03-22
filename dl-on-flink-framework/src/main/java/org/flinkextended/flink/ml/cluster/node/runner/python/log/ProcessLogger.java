/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.util.ShellExec;

import org.mortbay.log.Log;

/**
 * ProcessLogger collects stdout and stderr of the given process and use the given ${@link
 * AbstractProcessOutputConsumer} to consume the stdout and stderr.
 */
public class ProcessLogger {
    private final String processIdentity;
    private final Process process;
    private final AbstractProcessOutputConsumer processOutputConsumer;

    public ProcessLogger(
            String processIdentity,
            Process process,
            AbstractProcessOutputConsumer processOutputConsumer) {
        this.processIdentity = processIdentity;
        this.process = process;
        this.processOutputConsumer = processOutputConsumer;
    }

    public void start_logging() {
        Log.info("Start logging process {} with {}", processIdentity, processOutputConsumer);
        Thread inLogger =
                new Thread(
                        new ShellExec.ProcessLogger(
                                process.getInputStream(),
                                processOutputConsumer.getStdOutConsumer()));
        Thread errLogger =
                new Thread(
                        new ShellExec.ProcessLogger(
                                process.getErrorStream(),
                                processOutputConsumer.getStdErrConsumer()));
        inLogger.setName(processIdentity + "-in-logger");
        inLogger.setDaemon(true);
        errLogger.setName(processIdentity + "-err-logger");
        errLogger.setDaemon(true);
        inLogger.start();
        errLogger.start();
    }
}
