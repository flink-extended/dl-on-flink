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

package org.flinkextended.flink.ml.cluster.storage;

import org.codehaus.plexus.util.FileUtils;

import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.List;

/**
 * A local file storage implementation of Storage that can support pseudo distributed deep learning
 * cluster.
 */
public class LocalFileStorageImpl implements Storage {

    private final String rootDir;
    private final FileChannel lockFileChannel;

    public LocalFileStorageImpl(String rootDir) {
        final Path valuePath = Paths.get(rootDir);
        if (!Files.exists(valuePath)) {
            throw new RuntimeException(String.format("%s doesn't exist", rootDir));
        }
        final Path rootPath = Paths.get(rootDir, "dl-on-flink-kv");
        try {
            try {
                Files.createDirectory(rootPath);
            } catch (FileAlreadyExistsException e) {
                // ignore
            }
            this.rootDir = rootPath.toString();
            this.lockFileChannel =
                    FileChannel.open(
                            Paths.get(this.rootDir, ".lock"),
                            StandardOpenOption.WRITE,
                            StandardOpenOption.CREATE);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public byte[] getValue(String path) throws IOException {
        synchronized (LocalFileStorageImpl.class) {
            try (FileLock lock = lockFileChannel.lock()) {
                final Path valuePath = Paths.get(rootDir, path);
                if (!Files.exists(valuePath)) {
                    return null;
                }
                return Files.readAllBytes(valuePath);
            }
        }
    }

    @Override
    public void setValue(String path, byte[] value) throws IOException {
        synchronized (LocalFileStorageImpl.class) {
            try (FileLock lock = lockFileChannel.lock()) {
                final Path valuePath = Paths.get(rootDir, path);
                Files.write(
                        valuePath,
                        value,
                        StandardOpenOption.WRITE,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.TRUNCATE_EXISTING);
            }
        }
    }

    @Override
    public void removeValue(String path) throws IOException {
        synchronized (LocalFileStorageImpl.class) {
            try (FileLock lock = lockFileChannel.lock()) {
                final Path valuePath = Paths.get(rootDir, path);
                Files.delete(valuePath);
            }
        }
    }

    @Override
    public List<String> listChildren(String path) throws IOException {
        throw new UnsupportedOperationException("List children is not supported");
    }

    @Override
    public boolean exists(String path) throws IOException {
        synchronized (LocalFileStorageImpl.class) {
            try (FileLock lock = lockFileChannel.lock()) {
                final Path valuePath = Paths.get(rootDir, path);
                return Files.exists(valuePath);
            }
        }
    }

    @Override
    public void clear() {
        try {
            FileUtils.deleteDirectory(rootDir);
            try {
                Files.createDirectory(Paths.get(rootDir));
            } catch (FileAlreadyExistsException e) {
                // ignore
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
