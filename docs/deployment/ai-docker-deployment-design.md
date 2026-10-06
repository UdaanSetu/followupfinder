# AI Docker Deployment Design Report

## Status

This document describes the proposed containerization design for the
FollowUpFinder AI component. It is a design only; no Docker image has been
built and no service implementation has been added yet.

## Existing AI Structure

```text
ai/
├── adapters/
│   ├── lora_full_gpu/
│   ├── lora_gpu_smoke/
│   ├── lora_round2_gpu/
│   └── lora_round3_gpu/
├── datasets/
├── inference/
│   ├── __init__.py
│   ├── inference.py
│   ├── model_loader.py
│   ├── parser.py
│   ├── prompt.py
│   ├── evaluate_lora*.py
│   └── models/
│       └── Qwen3-0.6B/
├── scripts/
├── training/
├── README.md
└── requirements.txt
```

There is currently no Dockerfile, FastAPI service, Docker Compose file,
Kubernetes manifest, or HTTP smoke test.

## Existing Inference Entry Point

```python
from ai.inference import extract_followup

result = extract_followup(user_text)
```

The current inference flow:

1. Loads the cached tokenizer, base model, and LoRA adapter.
2. Builds adapter-compatible user-only chat messages.
3. Applies the Qwen chat template.
4. Tokenizes the input.
5. Generates deterministically with `max_new_tokens=300`.
6. Decodes only newly generated tokens.
7. Parses the JSON response.

Relevant files:

- `ai/inference/inference.py`
- `ai/inference/model_loader.py`
- `ai/inference/prompt.py`
- `ai/inference/parser.py`

## Model and Adapter Locations

### Base model

```text
ai/inference/models/Qwen3-0.6B/
```

Approximate size: **1.5 GB**.

### Production adapter

```text
ai/adapters/lora_round3_gpu/
```

Approximate size: **58 MB**, including metadata and checkpoint-related files.

The adapter weights must remain unchanged.

## Existing Dependencies

Current `ai/requirements.txt`:

```text
torch
transformers
peft
```

The HTTP service additionally requires:

```text
fastapi
uvicorn[standard]
```

Dependency versions should be based on the existing working environment.
Packages must not be installed globally.

## Proposed Docker Architecture

```text
Client or FastAPI backend
          |
          v
   AI HTTP service
          |
          v
   extract_followup()
          |
          v
 Qwen3-0.6B + LoRA adapter
          |
          v
       CPU by default
```

The service should:

- Run on CPU by default.
- Expose an HTTP API.
- Load the model once at startup.
- Preserve the current `extract_followup()` behavior.
- Provide a health endpoint.
- Support graceful startup and shutdown.
- Allow model and adapter paths to be configured through environment variables.
- Permit future GPU deployment without changing the API.

## Proposed Files

```text
ai/
├── Dockerfile
├── .dockerignore
├── service.py
├── service-requirements.txt
└── tests/
    └── test_service.py
```

An optional `ai/docker-compose.yml` may be added later for local development.

## Proposed Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FOLLOWUPFINDER_DEVICE=cpu \
    FOLLOWUPFINDER_BASE_MODEL_PATH=/models/Qwen3-0.6B \
    FOLLOWUPFINDER_ADAPTER_PATH=/models/lora-round3

WORKDIR /app

COPY ai/requirements.txt /app/ai/requirements.txt
COPY ai/service-requirements.txt /app/ai/service-requirements.txt

RUN pip install --no-cache-dir \
    -r /app/ai/requirements.txt \
    -r /app/ai/service-requirements.txt

COPY ai/inference /app/ai/inference
COPY ai/service.py /app/ai/service.py

EXPOSE 8000

CMD ["uvicorn", "ai.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

The Qwen base model should not be baked into the image. It should be mounted
as a read-only volume. The adapter may be mounted read-only or packaged into
the image according to the distribution policy.

## Proposed HTTP API

### `GET /health`

Ready response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cpu"
}
```

The endpoint should return HTTP `503` while the model is unavailable.

### `POST /extract`

Request:

```json
{
  "text": "Rahul ko quotation bhej diya, Friday ko call karna hai."
}
```

Response:

```json
{
  "contact": {
    "name": null,
    "organization": null
  },
  "event": {
    "type": null,
    "description": null,
    "amount": null,
    "currency": null,
    "status": null
  },
  "followup": {
    "required": false,
    "action": null,
    "date_expression": null
  }
}
```

Pydantic request and response models should validate the service boundary
without changing `extract_followup()` behavior.

## Environment Variables

Recommended variables:

```text
FOLLOWUPFINDER_DEVICE=cpu
FOLLOWUPFINDER_BASE_MODEL_PATH=/models/Qwen3-0.6B
FOLLOWUPFINDER_ADAPTER_PATH=/models/lora-round3
FOLLOWUPFINDER_HOST=0.0.0.0
FOLLOWUPFINDER_PORT=8000
```

The loader should use these values when provided and retain repository-relative
paths as development defaults.

## CPU Mode

CPU mode is enabled by default:

```text
FOLLOWUPFINDER_DEVICE=cpu
```

The loader should:

- Select `torch.device("cpu")`.
- Use `torch.float32`.
- Load the model once.
- Move the LoRA-wrapped model to CPU.
- Reuse the loaded model for all requests.

The container should use one worker by default to avoid loading duplicate
copies of the approximately 1.5 GB base model.

## Future GPU Mode

The API does not need to change for GPU deployment. A future deployment can
set:

```text
FOLLOWUPFINDER_DEVICE=cuda
```

and run the container with the NVIDIA Container Toolkit:

```bash
docker run --gpus all ...
```

GPU support remains an infrastructure configuration change. The existing
loader can select CUDA and use `torch.bfloat16` on CUDA-capable devices.

## Startup and Shutdown Lifecycle

The service should use a FastAPI lifespan handler:

1. Start the process.
2. Load the tokenizer, base model, and adapter once.
3. Mark the service ready.
4. Serve `/extract`.
5. Release references and exit cleanly during shutdown.

This makes readiness explicit and avoids model-loading latency on the first
request.

## Model Artifact Considerations

### Qwen base model

The base model is approximately 1.5 GB and should remain outside the Docker
image. Mount it read-only to avoid:

- Large image sizes.
- Slow builds and transfers.
- Registry storage costs.
- Duplicate model copies across image versions.

The root `.gitignore` excludes:

```text
ai/inference/models/Qwen3-0.6B/
```

### LoRA adapter

The production adapter is approximately 58 MB including related files. The
service needs only:

```text
ai/adapters/lora_round3_gpu/
```

Training checkpoints and optimizer state are not required for serving.

### Performance

CPU inference will be slower than GPU inference. The initial service should
use one worker and one model instance per container.

## Files to Modify During Implementation

Expected minimal changes:

```text
ai/inference/model_loader.py
```

Purpose:

- Add environment-variable overrides for model and adapter paths.
- Retain current repository-relative defaults.
- Preserve device, dtype, and loading behavior.

Potentially:

```text
ai/README.md
```

Purpose:

- Document Docker usage.
- Document the HTTP API.
- Document mounted model and adapter paths.

## Files That Must Remain Untouched

- `ai/inference/models/Qwen3-0.6B/`
- `ai/adapters/lora_round3_gpu/`
- All adapter `.safetensors` files.
- All training scripts under `ai/training/`.
- All datasets under `ai/datasets/`.
- All evaluation results.
- Existing prompt behavior.
- Existing parser behavior.
- Existing `extract_followup()` behavior.
- The existing Python environment.

## Architectural Boundary

The AI service performs language understanding only:

```text
User text
  -> AI inference
  -> structured JSON
  -> FastAPI/Pydantic validation
  -> entity resolution
  -> date resolution
  -> business rules
  -> MongoDB
```

The AI service must not:

- Connect directly to MongoDB.
- Search contacts.
- Create database records.
- Resolve database IDs.
- Resolve relative dates.
- Send reminders.
- Make business decisions.
- Call external APIs.

## Current Status

- Design inspected and documented.
- No Docker image built.
- No service implementation added.
- No packages installed.
- No model or adapter files changed.
- No datasets or evaluation results deleted.
- No commit or push performed.
