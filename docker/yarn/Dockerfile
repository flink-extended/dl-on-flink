#
# Copyright 2022 Deep Learning on Flink Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from prographerj/centos7-hadoop:latest

USER root
COPY bashrc /root/.bashrc
ADD core-site.xml /usr/local/hadoop/etc/hadoop/core-site.xml
ADD yarn-site.xml /usr/local/hadoop/etc/hadoop/yarn-site.xml
ADD slaves /usr/local/hadoop/etc/hadoop/slaves
ADD bootstrap.sh /etc/bootstrap.sh
RUN chmod 777 /etc/bootstrap.sh &&\
    yum clean all &&\
    yum -y install wget &&\
    yum -y install unzip &&\
    yum -y install zip &&\
    yum -y install net-tools &&\
    cd /opt &&\
    wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink/package/flink-1.8-SNAPSHOT.tgz &&\
    tar -zxvf flink-1.8-SNAPSHOT.tgz &&\
    mv flink-1.8-SNAPSHOT flink &&\
    rm -f flink-1.8-SNAPSHOT.tgz &&\
    cp flink/opt/* flink/lib/
ENV HADOOP_HOME=/usr/local/hadoop/ HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop/ HADOOP_HDFS_HOME=/usr/local/hadoop/

EXPOSE 8088
