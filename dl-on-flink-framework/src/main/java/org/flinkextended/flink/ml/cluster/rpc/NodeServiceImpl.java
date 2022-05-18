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

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.proto.ContextProto;
import org.flinkextended.flink.ml.proto.ContextRequest;
import org.flinkextended.flink.ml.proto.ContextResponse;
import org.flinkextended.flink.ml.proto.FinishWorkerResponse;
import org.flinkextended.flink.ml.proto.GetFinishNodeResponse;
import org.flinkextended.flink.ml.proto.NodeRestartRequest;
import org.flinkextended.flink.ml.proto.NodeRestartResponse;
import org.flinkextended.flink.ml.proto.NodeServiceGrpc;
import org.flinkextended.flink.ml.proto.NodeSimpleRequest;
import org.flinkextended.flink.ml.proto.NodeSimpleResponse;
import org.flinkextended.flink.ml.proto.NodeSpecRequest;
import org.flinkextended.flink.ml.proto.NodeSpecResponse;
import org.flinkextended.flink.ml.proto.NodeStopRequest;
import org.flinkextended.flink.ml.proto.NodeStopResponse;
import org.flinkextended.flink.ml.util.IpHostUtil;

import io.grpc.stub.StreamObserver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

/** machine learning cluster node service. */
public class NodeServiceImpl extends NodeServiceGrpc.NodeServiceImplBase {

    private static final Logger LOG = LoggerFactory.getLogger(NodeServiceImpl.class);

    private final NodeServer server;
    private final MLContext mlContext;
    private final AMClientFactory amClientFactory;

    public NodeServiceImpl(NodeServer server, MLContext mlContext) {
        this(server, mlContext, () -> AMRegistry.getAMClient(mlContext));
    }

    public NodeServiceImpl(
            NodeServer server, MLContext mlContext, AMClientFactory amClientFactory) {
        this.server = server;
        this.mlContext = mlContext;
        this.amClientFactory = amClientFactory;
    }

    /**
     * handle get node info request.
     *
     * @param request NodeSpecRequest
     * @param responseObserver
     */
    @Override
    public void getNodeSpec(
            NodeSpecRequest request, StreamObserver<NodeSpecResponse> responseObserver) {
        super.getNodeSpec(request, responseObserver);
    }

    /**
     * handle node restart request and restart machine learning runner.
     *
     * @param request NodeRestartRequest
     * @param responseObserver
     */
    @Override
    public void nodeRestart(
            NodeRestartRequest request, StreamObserver<NodeRestartResponse> responseObserver) {
        LOG.info(mlContext.getIdentity() + " receive restart");
        NodeRestartResponse restartResponse =
                NodeRestartResponse.newBuilder()
                        .setCode(RpcCode.OK.ordinal())
                        .setMessage(mlContext.getIdentity())
                        .build();
        responseObserver.onNext(restartResponse);
        responseObserver.onCompleted();
        server.setAmCommand(NodeServer.AMCommand.RESTART);
    }

    /**
     * handle stop node request, stop machine learning node.
     *
     * @param request NodeStopRequest.
     * @param responseObserver
     */
    @Override
    public void nodeStop(
            NodeStopRequest request, StreamObserver<NodeStopResponse> responseObserver) {
        NodeStopResponse response =
                NodeStopResponse.newBuilder().setCode(RpcCode.OK.ordinal()).setMessage("").build();
        String localIp = null;
        try {
            localIp = IpHostUtil.getIpAddress();
        } catch (Exception e) {
            e.printStackTrace();
        }
        LOG.info(
                "Received node stop request for {}. This node is {}:{}",
                mlContext.getIdentity(),
                localIp,
                String.valueOf(server.getPort()));
        server.setAmCommand(NodeServer.AMCommand.STOP);
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    /**
     * handle get context request and return current machine learning context.
     *
     * @param request ContextRequest
     * @param responseObserver
     */
    @Override
    public void getContext(
            ContextRequest request, StreamObserver<ContextResponse> responseObserver) {
        ContextProto contextProto =
                mlContext.getContextProto() == null
                        ? mlContext.toPB()
                        : mlContext.getContextProto();
        ContextResponse res =
                ContextResponse.newBuilder()
                        .setCode(0)
                        .setContext(contextProto)
                        .setMessage("")
                        .build();
        responseObserver.onNext(res);
        responseObserver.onCompleted();
    }

    /**
     * handle get finished worker list request and return finished worker list.
     *
     * @param request NodeSimpleRequest.
     * @param responseObserver
     */
    @Override
    public void getFinishWorker(
            NodeSimpleRequest request, StreamObserver<FinishWorkerResponse> responseObserver) {
        try (AMClient amClient = amClientFactory.getAMClient()) {
            GetFinishNodeResponse response = amClient.getFinishedWorker(0);

            FinishWorkerResponse.Builder builder =
                    FinishWorkerResponse.newBuilder().setCode(0).setMessage("");
            for (Integer index : response.getWorkersList()) {
                builder.addWorkers(index);
            }
            responseObserver.onNext(builder.build());
            responseObserver.onCompleted();
        } catch (IOException e) {
            e.printStackTrace();
            FinishWorkerResponse.Builder builder =
                    FinishWorkerResponse.newBuilder().setCode(1).setMessage(e.getMessage());
            responseObserver.onNext(builder.build());
            responseObserver.onCompleted();
        }
    }

    /**
     * handle stop job request and stop the machine learning cluster.
     *
     * @param request NodeSimpleRequest.
     * @param responseObserver
     */
    @Override
    public void finishJob(
            NodeSimpleRequest request, StreamObserver<NodeSimpleResponse> responseObserver) {
        NodeSimpleResponse.Builder builder = NodeSimpleResponse.newBuilder();
        try (AMClient amClient = amClientFactory.getAMClient()) {
            amClient.stopJob(0, mlContext.getRoleName(), mlContext.getIndex());
            builder.setCode(0);
            builder.setMessage("");
            responseObserver.onNext(builder.build());
        } catch (IOException e) {
            e.printStackTrace();
            builder.setCode(1);
            builder.setMessage(e.getMessage());
            responseObserver.onNext(builder.build());
        }
        responseObserver.onCompleted();
    }

    /** Factory for {@link AMClient}. */
    public interface AMClientFactory {
        public AMClient getAMClient() throws IOException;
    }
}
