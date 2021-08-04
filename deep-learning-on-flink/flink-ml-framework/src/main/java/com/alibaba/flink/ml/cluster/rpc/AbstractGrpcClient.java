package com.alibaba.flink.ml.cluster.rpc;

import io.grpc.ConnectivityState;
import io.grpc.ManagedChannel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Closeable;
import java.time.Duration;
import java.util.concurrent.TimeUnit;

public abstract class AbstractGrpcClient implements Closeable {
	private static final Logger LOG = LoggerFactory.getLogger(AbstractGrpcClient.class);

	protected final String host;
	protected final int port;
	protected final ManagedChannel grpcChannel;

	public AbstractGrpcClient(String host, int port, ManagedChannel grpcChannel) {
		this.host = host;
		this.port = port;
		this.grpcChannel = grpcChannel;
	}

	/**
	 * The name of the server that the client is connecting to. The name is used mainly for logging purpose.
	 * @return he name of the server that the client is connecting to.
	 */
	abstract String serverName();

	@Override
	public void close() {
		LOG.info("close {} client", serverName());
		if (grpcChannel != null) {
			grpcChannel.shutdown();
			try {
				boolean res = grpcChannel.awaitTermination(2, TimeUnit.MINUTES);
				LOG.info("{} client channel termination: {}", serverName(), res);
			} catch (InterruptedException e) {
				LOG.error("{} client termination interrupted.", serverName(), e);
			}
		}
	}

	/**
	 * Wait until the grpc channel is ready.
	 * @param duration time out
	 * @return the boolean indicating the grpc channel is ready or not when return.
	 * @throws InterruptedException if the current thread is interrupted
	 */
	public boolean waitForReady(Duration duration) throws InterruptedException {
		final long deadline = System.currentTimeMillis() + duration.toMillis();
		while (grpcChannel.getState(true) != ConnectivityState.READY) {
			if (System.currentTimeMillis() > deadline) {
				return false;
			}
			//noinspection BusyWait
			Thread.sleep(1000);
		}
		return true;
	}

	public String getHost() {
		return host;
	}

	public int getPort() {
		return port;
	}
}
