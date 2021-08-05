##
## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##

# DESCRIPTION: Basic Flink AI Flow image
FROM python:3.7-slim-buster AS builder

RUN python3 -m pip install wheel \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends npm \
    && npm install --global yarn \
    && mkdir /tmp/dist

WORKDIR /flink-ai-flow

COPY . /flink-ai-flow
ARG ai_flow_package_type
RUN if [ "x$ai_flow_package_type" = "x" ]; then \
    bash build_ai_flow_package.sh wheel; \
    else bash build_ai_flow_package.sh wheel mini; fi
RUN cp dist/* /tmp/dist
RUN cd lib/notification_service && python3 setup.py bdist_wheel && cp dist/* /tmp/dist

FROM python:3.7-slim-buster
# AIFlow
ARG AIFLOW_HOME=/usr/local/aiflow
ENV AIFLOW_HOME=${AIFLOW_HOME}

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

COPY ./examples /opt/aiflow/examples

COPY --from=builder /tmp/dist /tmp/dist
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev curl ssh vim unzip gcc \
    && pip install --no-cache-dir /tmp/dist/* \
    && apt-get purge --auto-remove -yqq gcc \
    && apt-get autoremove -yqq --purge \
    && apt-get clean

USER root
WORKDIR ${AIFLOW_HOME}
