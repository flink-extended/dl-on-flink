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

package org.flinkextended.flink.ml.operator.util;

import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.cache.DistributedCache;
import org.apache.flink.api.common.functions.RuntimeContext;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.Preconditions;

import com.google.common.base.Joiner;
import org.apache.commons.lang3.StringUtils;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** before execute python script, prepare python script. */
public class PythonFileUtil {
    private static final String SPLITTER = ",";

    /**
     * set machine learning job run python script.
     *
     * @param flinkEnv flink StreamExecutionEnvironment.
     * @param mlConfig machine learning cluster configuration.
     */
    public static void registerPythonFiles(StreamExecutionEnvironment flinkEnv, MLConfig mlConfig)
            throws IOException {
        if (mlConfig.getProperties().containsKey(MLConstants.REMOTE_CODE_ZIP_FILE)) {
            mlConfig.addProperty(MLConstants.USER_ENTRY_PYTHON_FILE, mlConfig.getPythonFiles()[0]);
        } else {
            List<String> files =
                    registerPythonLibFilesIfNotExist(flinkEnv, mlConfig.getPythonFiles());
            String fileStr = Joiner.on(SPLITTER).join(files);
            mlConfig.addProperty(MLConstants.PYTHON_FILES, fileStr);
        }
    }

    /**
     * copy machine learning job run python script to flink task local disk.
     *
     * @param runtimeContext flink operator RuntimeContext.
     * @param mlContext machine learning node runtime context.
     */
    public static void preparePythonFilesForExec(RuntimeContext runtimeContext, MLContext mlContext)
            throws IOException {
        if (mlContext.useDistributeCache()) {
            String filesStr = mlContext.getProperties().get(MLConstants.PYTHON_FILES);
            if (StringUtils.isEmpty(filesStr)) {
                return;
            }
            String[] files = filesStr.split(SPLITTER);
            DistributedCache cache = runtimeContext.getDistributedCache();
            // the temp dir to hold all files
            Path dir = mlContext.createTempDir("ml_on_flink_");

            // copy all files to temp dir
            for (String file : files) {
                File f = cache.getFile(file);
                Files.copy(f.toPath(), dir.resolve(file));
            }
            mlContext.setPythonDir(dir);
            mlContext.setPythonFiles(files);
        }
    }

    public static List<String> registerPythonLibFilesIfNotExist(
            StreamExecutionEnvironment env, String... userPyLibs) throws IOException {
        Tuple2<Map<String, URI>, List<String>> tuple2 = convertFiles(userPyLibs);
        Map<String, URI> files = tuple2.f0;
        files.forEach(
                (name, uri) ->
                        registerCachedFileIfNotExist(env.getCachedFiles(), uri.getPath(), name));
        return tuple2.f1;
    }

    private static Tuple2<Map<String, URI>, List<String>> convertFiles(String... userPyLibs) {
        // flink requires we register the file with a URI
        Map<String, URI> keyToURI = new HashMap<>();
        List<String> fileKeys = new ArrayList<>();
        for (String file : userPyLibs) {
            URI uri = URI.create(file);
            if (uri.getScheme() == null) {
                uri = Paths.get(file).toUri();
            }

            // keys should be consistent with JobGraph.addUserArtifact
            final String fileKey =
                    uri.getFragment() != null
                            ? uri.getFragment()
                            : Paths.get(uri).getFileName().toString();
            keyToURI.put(fileKey, uri);
            fileKeys.add(fileKey);
        }
        return new Tuple2<>(keyToURI, fileKeys);
    }

    private static void registerCachedFileIfNotExist(
            List<Tuple2<String, DistributedCache.DistributedCacheEntry>> cachedFiles,
            String filePath,
            String fileKey) {
        if (cachedFiles.stream().noneMatch(t -> t.f0.equals(fileKey))) {
            cachedFiles.add(
                    new Tuple2<>(
                            fileKey, new DistributedCache.DistributedCacheEntry(filePath, false)));
        } else {
            final Tuple2<String, DistributedCache.DistributedCacheEntry> existEntry =
                    cachedFiles.stream().filter(t -> t.f0.equals(fileKey)).findFirst().orElse(null);
            assert existEntry != null;
            Preconditions.checkState(
                    existEntry.f1.filePath.equals(filePath),
                    "Fail to register cache file with key %s file path %s, the same key has been registered with path %s",
                    fileKey,
                    filePath,
                    existEntry.f1.filePath);
        }
    }
}
