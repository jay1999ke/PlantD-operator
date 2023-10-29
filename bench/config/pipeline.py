import os
from time import sleep
from multiprocessing import Queue, Process

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from bench.config.topology import Config, StandardTopology, ConfigKeys, Node

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("test-pipeline")

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
tp: TracerProvider =  trace.get_tracer_provider()
tp.add_span_processor(BatchSpanProcessor(otlp_exporter))

class StandardStage:

    def __init__(self, index, cfg: Config, isLast: bool, isFirst: bool) -> None:
        self.index: int = index
        self.cfg = cfg
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
        while True:
            message = self.queue.get()
            with tracer.start_as_current_span(f'Stage{self.index}', kind=SpanKind.SERVER) as span:
                sleep(self.cfg.latency_ms)
                if not self.isLast:
                    self.out_queue.put(message)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.index)
    

def GeneratePipeline(self, cfg: Config, node: Node):
    if cfg.type == ConfigKeys.StandardTopology:
        topology = StandardTopology(config=cfg)