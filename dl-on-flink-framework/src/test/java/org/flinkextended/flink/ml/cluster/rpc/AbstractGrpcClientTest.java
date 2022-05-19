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

package org.flinkextended.flink.ml.cluster.rpc;

import io.grpc.ConnectivityState;
import io.grpc.ManagedChannel;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.anyLong;
import static org.mockito.Matchers.notNull;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/** Unit test for {@link AbstractGrpcClient}. */
public class AbstractGrpcClientTest {
    private static final Logger LOG = LoggerFactory.getLogger(AbstractGrpcClientTest.class);

    public static final String TEST_HOST = "localhost";
    public static final int TEST_PORT = 8080;
    TestGrpcClient grpcClient;
    private ManagedChannel channel;

    @Before
    public void setUp() throws Exception {
        grpcClient = new TestGrpcClient(TEST_HOST, TEST_PORT);
        channel = grpcClient.getChannel();
    }

    @Test
    public void testGetHost() {
        assertEquals(TEST_HOST, grpcClient.getHost());
    }

    @Test
    public void testGetPort() {
        assertEquals(TEST_PORT, grpcClient.getPort());
    }

    @Test
    public void testClose() throws InterruptedException {
        grpcClient.close();
        verify(channel).shutdown();
        verify(channel).awaitTermination(anyLong(), notNull(TimeUnit.class));
    }

    @Test
    public void testCloseHandleInterruptedException() throws InterruptedException {
        when(channel.awaitTermination(anyLong(), notNull(TimeUnit.class)))
                .thenThrow(new InterruptedException("Fail intentionally"));
        grpcClient.close();
    }

    @Test
    public void testWaitForReady() throws InterruptedException {
        when(channel.getState(true)).thenReturn(ConnectivityState.CONNECTING);
        assertFalse(grpcClient.waitForReady(Duration.ofSeconds(1)));
        when(channel.getState(true)).thenReturn(ConnectivityState.READY);
        assertTrue(grpcClient.waitForReady(Duration.ofSeconds(10)));
    }

    @Test
    public void testWaitForReadyThrowException() throws InterruptedException {
        Thread t = Thread.currentThread();
        Thread interruptThread = new Thread(t::interrupt);
        boolean exception = false;
        interruptThread.start();
        try {
            grpcClient.waitForReady(Duration.ofSeconds(10));
        } catch (InterruptedException e) {
            // expected
            LOG.info("expected exception: ", e);
            exception = true;
        }
        assertTrue(exception);
        interruptThread.join();
    }

    private static class TestGrpcClient extends AbstractGrpcClient {

        public TestGrpcClient(String host, int port) {
            super(host, port, Mockito.mock(ManagedChannel.class));
        }

        public ManagedChannel getChannel() {
            return grpcChannel;
        }

        @Override
        String serverName() {
            return null;
        }
    }
}
