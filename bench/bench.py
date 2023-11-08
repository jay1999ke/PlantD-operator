import io
import csv
import sys
import uvicorn
import zipfile

from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from config.pipeline import GeneratePipeline, StandardPipeline, parseConfig

app = FastAPI()

sample = {
    "Type": "Standard",
    "Latency": 10,
    "FailRate": 0.01,
    "StageCount": 4
}

test_pipeline: StandardPipeline = GeneratePipeline(parseConfig(sample))

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        zip_data = await file.read()

        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(".csv"):
                    csv_data = zip_ref.read(file_info)
                    reader = csv.reader(csv_data.decode('utf-8').splitlines())
                    for row in reader:
                        print(row)
                        test_pipeline.processRequest(row)

        return {"status": "Success!", "code": 200}
    except Exception as e:
        print(e, file=sys.stderr)
        return {"status": "Failed to upload!", "code": 500}

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app",
                host="0.0.0.0", port=3000, workers=1)