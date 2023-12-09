import os
from typing import List
from time import sleep, time
from multiprocessing import Queue, Process

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from config.topology import Config, StandardTopology, ConfigKeys, parseConfig, Node

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("test-pipeline")

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
tp: TracerProvider = trace.get_tracer_provider()
tp.add_span_processor(BatchSpanProcessor(otlp_exporter))

def get_parent_context(trace_id, span_id):
    parent_context = SpanContext(
        trace_id=trace_id,
        span_id=span_id,
        is_remote=True,
        trace_flags=TraceFlags(0x01)
    )
    return trace.set_span_in_context(NonRecordingSpan(parent_context))



class StandardStage:

    def __init__(self, index, node: Node, isLast: bool, isFirst: bool) -> None:
        self.index: int = index
        self.node = node
        self.queue = Queue()
        self.out_queue = None
        self.worker = Process(target=self.task)
        self.isFirst = isFirst
        self.isLast = isLast

    def start(self):
        self.worker.daemon = True
        self.worker.start()

    def setOutQueue(self, queue: Queue):
        self.out_queue = queue

    def task(self):
        counter = 0
        curr = time()
        while True:
            message = self.queue.get()
            if counter % 1000 == 0:
                print("stage: ", self.index, " completed ", counter, " requests in ", time() - curr ," secs.")
                curr = time()
                counter = 0
            try:
                with tracer.start_as_current_span(f'Stage{self.index}', kind=SpanKind.SERVER) as span:
                    sleep(self.node.latency_ms)
                    if not self.isLast:
                        self.out_queue.put(message)
                counter += 1
            except Exception as ex:
                print(ex)
                import traceback
                traceback.print_exc()


    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.index)


class Pipeline:
    pass


class StandardPipeline(Pipeline):

    def __init__(self, topology: StandardTopology, config: Config) -> None:
        super().__init__()
        self.topology = topology
        self.config = config
        self.stages: List[StandardStage] = []
        self.createPipeline()

    def createPipeline(self):
        # create root stage
        self.root = StandardStage(
            index=1,
            node=self.topology.root,
            isLast=(self.config.stage_count == 1),
            isFirst=True
        )
        self.stages.append(self.root)
        self.createStage(self.root, self.topology.root)

        for stage in self.stages:
            stage.start()

        # ensure start-up
        sleep(1)

    def createStage(self, parentStage: StandardStage, parentNode: Node):
        if len(parentNode.children) > 0:
            childNode: Node = parentNode.children[0]
            isLast = len(childNode.children) == 0
            stage = StandardStage(
                index=childNode.stage_index,
                node=childNode,
                isFirst=False,
                isLast=isLast
            )
            parentStage.out_queue = stage.queue
            self.stages.append(stage)
            self.createStage(stage, childNode)

    def processRequest(self, request):
        self.root.queue.put(request)

def GeneratePipeline(cfg: Config) -> Pipeline:
    if cfg.type == ConfigKeys.type_standard:
        topology = StandardTopology(config=cfg)
        return StandardPipeline(topology, cfg)


if __name__ == "__main__":

    sample = {
        "Type": "Standard",
        "Latency": 10,
        "FailRate": 0.01,
        "StageCount": 3
    }

    test_pipeline = GeneratePipeline(parseConfig(sample))
    sleep(10)
