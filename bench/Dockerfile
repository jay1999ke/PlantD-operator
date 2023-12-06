FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
RUN python3 -m pip install --no-cache-dir --upgrade pip

WORKDIR /bench

COPY requirements.txt bench.py /bench/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["uvicorn", "bench:app", "--host", "0.0.0.0", "--port", "3000"]