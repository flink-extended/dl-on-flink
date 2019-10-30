from enum import Enum
from python.flink_ml_workflow.vertex.base_vertex import *
from python.flink_ml_workflow.vertex.transformer import *
from python.flink_ml_workflow.vertex.execution import *


class HistoryType(str, Enum):
    EXECUTION = "EXECUTION"
    WORKFLOW = "WORKFLOW"


class History(BaseVertex):
    def __init__(self,
                 name,
                 history_type: HistoryType,
                 start_time,
                 end_time,
                 uri: str,
                 refer_id=0,
                 refer_name="",
                 properties: dict = None):
        super(History, self).__init__(name, properties)
        self.history_type = history_type
        self.start_time = start_time
        self.end_time = end_time
        self.uri = uri
        self.refer_id = refer_id
        self.refer_name = refer_name

    def to_proto(self):
        history_proto = HistoryProto()
        return self.set_proto(history_proto)

    def set_proto(self, history_proto):
        history_proto.meta.name = self.name
        for i in self.properties:
            history_proto.meta.properties[i] = self.properties[i]

        if self.history_type == HistoryType.EXECUTION:
            history_proto.type = HistoryTypeProto.EXECUTION
        else:
            history_proto.type = HistoryTypeProto.WORKFLOW

        history_proto.startTime = self.start_time
        history_proto.endTime = self.end_time
        history_proto.uri = self.uri
        history_proto.referId = self.refer_id
        history_proto.referName = self.refer_name
        return history_proto


if __name__ == "__main__":
    import time
    millis = int(round(time.time() * 1000))
    history = History(name="history",
                      history_type=HistoryType.EXECUTION,
                      start_time=millis,
                      end_time=millis+5*1000,
                      uri="./log",
                      refer_name="execution")

    print(history.to_json())
