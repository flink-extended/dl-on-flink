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
from flink:1.6-hadoop27

USER root

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /opt
# RUN cp opt/flink-table_2.11-1.6.0.jar lib/

# set up hadoop
RUN wget https://flink-ai-extended.oss-cn-beijing.aliyuncs.com/hadoop-2.8.0.tar.gz; tar xf hadoop-2.8.0.tar.gz; rm -f hadoop-2.8.0.tar.gz
ENV HADOOP_HDFS_HOME /opt/hadoop-2.8.0
ENV HADOOP_HOME /opt/hadoop-2.8.0
COPY core-site.xml /opt/hadoop-2.8.0/etc/hadoop/

# install flink 1.11
RUN rm -rf /opt/flink; wget https://flink-ai-extended.oss-cn-beijing.aliyuncs.com/flink-1.11.0-bin-scala_2.11.tgz
RUN tar xf flink-1.11.0-bin-scala_2.11.tgz
RUN mv flink-1.11.0 flink
RUN rm -f flink-1.11.0-bin-scala_2.11.tgz

#RUN rm -rf /opt/flink; wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink/package/flink-1.8-SNAPSHOT.tgz
#RUN tar xf flink-1.8-SNAPSHOT.tgz
#RUN mv flink-1.8-SNAPSHOT flink
#RUN rm -f flink-1.8-SNAPSHOT.tgz
RUN cp -r flink/opt/* flink/lib/

ENV HADOOP_CLASSPATH=/opt/hadoop-2.8.0/etc/hadoop:/opt/hadoop-2.8.0/share/hadoop/common/lib/*:/opt/hadoop-2.8.0/share/hadoop/common/*:/opt/hadoop-2.8.0/share/hadoop/hdfs:/opt/hadoop-2.8.0/share/hadoop/hdfs/lib/*:/opt/hadoop-2.8.0/share/hadoop/hdfs/*:/opt/hadoop-2.8.0/share/hadoop/yarn/lib/*:/opt/hadoop-2.8.0/share/hadoop/yarn/*:/opt/hadoop-2.8.0/share/hadoop/mapreduce/lib/*:/opt/hadoop-2.8.0/share/hadoop/mapreduce/*:/opt/hadoop-2.8.0/share/hadoop/common/:/opt/hadoop-2.8.0/share/hadoop/common/lib/:/opt/hadoop-2.8.0/share/hadoop/common/lib/:/opt/hadoop-2.8.0/share/hadoop/hdfs/:/opt/hadoop-2.8.0/share/hadoop/hdfs/lib/:/opt/hadoop-2.8.0/share/hadoop/yarn/:/opt/hadoop-2.8.0/share/hadoop/yarn/lib/:/opt/hadoop-2.8.0/contrib/capacity-scheduler/*.jar

# set up apt
COPY sources.list /etc/apt/
RUN apt-get update

# set up java
RUN apt-get install -y openjdk-8-jdk
ENV JAVA_HOME /docker-java-home

# install dev packages
RUN apt-get install -y apt-utils vim python3 python3-pip zip net-tools procps \
    && ln -sf `which python3` /bin/python \
    && ln -sf `which pip3` /bin/pip
RUN apt-get install -y openjdk-8-dbg gdb git cmake python3-dbg
RUN apt-get install -y libz-dev
RUN mkdir /root/.pip
COPY pip.conf /root/.pip/
RUN pip install virtualenv

COPY bashrc /root/.bashrc
COPY vimrc /root/.vimrc
COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["help"]

ENV DEBIAN_FRONTEND teletype
