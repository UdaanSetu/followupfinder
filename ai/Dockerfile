FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FOLLOWUPFINDER_DEVICE=cuda \
    FOLLOWUPFINDER_BASE_MODEL_PATH=/models/Qwen3-0.6B \
    FOLLOWUPFINDER_ADAPTER_PATH=/models/lora-round3

WORKDIR /app

COPY requirements.txt /app/ai/requirements.txt
COPY service-requirements.txt /app/ai/service-requirements.txt

RUN pip install --no-cache-dir \
    -r /app/ai/requirements.txt \
    -r /app/ai/service-requirements.txt

COPY inference /app/ai/inference
COPY service.py /app/ai/service.py

EXPOSE 8000

CMD ["uvicorn", "ai.service:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
