# AI Docker Deployment Implementation Report

## Project

FollowUpFinder AI

## Scope

The CPU-first Docker deployment design was implemented without:

- Retraining any model.
- Running GPU training.
- Modifying model weights.
- Modifying LoRA adapter weights.
- Deleting datasets or evaluation results.
- Installing packages globally.
- Committing or pushing to GitHub.

## Files Created

- `ai/Dockerfile`
- `ai/.dockerignore`
- `ai/service.py`
- `ai/service-requirements.txt`
- `ai/tests/test_service.py`

## Files Modified

- `ai/inference/model_loader.py`

The loader now supports:

```text
FOLLOWUPFINDER_DEVICE
FOLLOWUPFINDER_BASE_MODEL_PATH
FOLLOWUPFINDER_ADAPTER_PATH
```

Existing repository-relative defaults remain in place.

The Dockerfile was corrected to use `ai/` as the build context:

```bash
docker build -f ai/Dockerfile -t followupfinder-ai:cpu ai
```

## Files Untouched

- Qwen3-0.6B base model.
- LoRA adapter weights.
- Training scripts.
- Datasets.
- Evaluation results.
- Prompt implementation.
- Parser implementation.
- `extract_followup()` behavior.
- Existing Python environment.

Protected artifact hashes remain unchanged:

```text
Qwen model:
f47f71177f32bcd101b7573ec9171e6a57f4d31148d38e382306f42996874b

LoRA adapter:
844fc15b4c4126e814f357de8d5941d144fb0f6bc8c7853eb4def260f0549287
```

## Docker Image

Intended image:

```text
followupfinder-ai:cpu
```

## Docker Build Result

The build was retried with the corrected AI build context, but Docker daemon
access remains unavailable:

```text
permission denied while trying to connect to the Docker API
at unix:///var/run/docker.sock
```

The Docker client is installed, but the Docker server cannot currently be
accessed by the active user.

No image was created.

## Container Result

No container was started because the Docker daemon was inaccessible.

Therefore the following could not yet be tested in a container:

- Container startup.
- Read-only model and adapter mounts.
- `/health`.
- `/extract`.
- Container memory usage.

## Implemented HTTP API

### Health

```http
GET /health
```

Expected response after model startup:

```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cpu"
}
```

### Extraction

```http
POST /extract
```

Request:

```json
{
  "text": "Rahul ko quotation bhej diya, Friday ko call karna hai."
}
```

The endpoint directly calls the existing:

```python
extract_followup(request.text)
```

No second extraction implementation was introduced.

Invalid or missing text returns HTTP `422`.

## Validation Results

Python syntax validation passed for:

- `ai/service.py`
- `ai/inference/model_loader.py`
- `ai/tests/test_service.py`

The existing environment does not contain `fastapi` or `pytest`, so HTTP test
execution was not possible without installing packages. No packages were
installed because the existing environment was required to remain unchanged.

Direct CPU inference through the existing public API was previously validated
for all three requested examples:

1. `Rahul ko 50k ka website quotation bhej diya, Friday ko call karna hai.`
2. `Gupta Traders ke liye 1 lakh ka order cancel ho gaya.`
3. `Ramesh se meeting kal schedule hai.`

The results matched the established direct inference behavior and passed the
structured JSON schema checks.

## Artifact Handling

The Docker build context excludes:

- Qwen3-0.6B base model.
- LoRA adapter directory.
- Datasets.
- Training scripts.
- Evaluation files.
- Python caches.

The first Docker deployment is intended to use read-only runtime mounts for the
base model and adapter.

## Current Readiness

The AI service code and Docker configuration are implemented, but deployment
validation is incomplete because Docker daemon access is blocked and the
existing environment lacks FastAPI and pytest.

The service is **not yet fully validated for Kubernetes deployment**. Once
Docker daemon permissions are fixed, the next steps are:

```bash
docker build -f ai/Dockerfile -t followupfinder-ai:cpu ai
docker run --rm \
  -p 8000:8000 \
  -e FOLLOWUPFINDER_DEVICE=cpu \
  -e FOLLOWUPFINDER_BASE_MODEL_PATH=/models/Qwen3-0.6B \
  -e FOLLOWUPFINDER_ADAPTER_PATH=/models/lora-round3 \
  -v /path/to/Qwen3-0.6B:/models/Qwen3-0.6B:ro \
  -v /path/to/lora_round3_gpu:/models/lora-round3:ro \
  followupfinder-ai:cpu
```

No Kubernetes manifests, Helm charts, Argo CD configuration, Jenkins
configuration, commit, or push was created.
