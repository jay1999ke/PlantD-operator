import io
import os
import csv
import sys
import uvicorn
import zipfile

from pathlib import Path
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from fastapi import FastAPI, UploadFile, File
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = FastAPI()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("test-pipeline")

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
tp: TracerProvider =  trace.get_tracer_provider()
tp.add_span_processor(BatchSpanProcessor(otlp_exporter))

def get_parent_context(trace_id, span_id):
	parent_context = SpanContext(
		trace_id=trace_id,
		span_id=span_id,
		is_remote=True,
		trace_flags=TraceFlags(0x01)
	)
	return trace.set_span_in_context(NonRecordingSpan(parent_context))

def process_csv_data(csv_data, context, csv_file_name):
    try:
        return {"status": "Success!", "code": 200}
    except Exception as e:
        context.span.set_status(Status(StatusCode.ERROR, description="Error processing CSV"))
        print(e, file=sys.stderr)
        return {"status": "Failed to process CSV!", "code": 500}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    with tracer.start_as_current_span("phase1", kind=SpanKind.SERVER) as span:
        try:
            zip_data = await file.read()

            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith(".csv"):
                        csv_data = zip_ref.read(file_info)
                        reader = csv.reader(csv_data.decode('utf-8').splitlines())
                        for row in reader:
                            print(row)     

            return {"status": "Success!", "code": 200}
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, description="Error during processing of zip file"))
            print(e, file=sys.stderr)
            return {"status": "Failed to upload!", "code": 500}

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=3000, workers=1)