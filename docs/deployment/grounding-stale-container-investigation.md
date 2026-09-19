# Grounding and Stale Container Investigation

## Summary

The incorrect API response was caused by a stale Docker container, not by a
failure in the current host-side grounding implementation.

The running container was started from an older `followupfinder-ai:cpu` image
that predates the grounding changes.

## Reported Input

```text
Ramesh ke saath meeting kal 3 baje scheduled hai.
```

## Incorrect Live API Response

```json
{
  "contact": {
    "name": "Ramesh",
    "organization": "RK Electricals"
  },
  "event": {
    "type": "meeting",
    "description": "2BHK flat",
    "amount": null,
    "currency": null,
    "status": "planned"
  },
  "followup": {
    "required": false,
    "action": null,
    "date_expression": null
  }
}
```

The organization and description were hallucinated, and the date expression
was missing.

## Host-Side Inspection

The current host inference path is:

```text
extract_followup()
  -> parse_model_output()
  -> ground_result()
  -> response
```

Current [inference.py](/home/ak/Downloads/followupfinder-ai(1)/followupfinder/ai/inference/inference.py)
contains:

```python
return ground_result(text, parse_model_output(generated_text))
```

Current [service.py](/home/ak/Downloads/followupfinder-ai(1)/followupfinder/ai/service.py)
calls:

```python
return extract_followup(request.text)
```

No alternate host implementation of `grounding.py`, `inference.py`, or
`service.py` was found.

## Host Grounding Isolation Test

The grounding function was tested directly with the model-like incorrect
result.

Input:

```text
Ramesh ke saath meeting kal 3 baje scheduled hai.
```

Host result:

```json
{
  "contact": {
    "name": "Ramesh",
    "organization": null
  },
  "event": {
    "type": "meeting",
    "description": null,
    "amount": null,
    "currency": null,
    "status": "planned"
  },
  "followup": {
    "required": false,
    "action": null,
    "date_expression": "kal 3 baje"
  }
}
```

This confirms that the current host [grounding.py](/home/ak/Downloads/followupfinder-ai(1)/followupfinder/ai/inference/grounding.py)
works as intended.

## Live Process Evidence

The service on port `8001` is backed by a process started with:

```text
docker run --name followupfinder-ai \
  -p 8001:8000 \
  ... \
  followupfinder-ai:cpu
```

The container process started at:

```text
Tue Sep 15 21:18:45 2026
```

The running process predates the current grounding implementation. Therefore,
the container is serving old code.

## Docker Access Limitation

Docker inspection and container management were blocked by:

```text
permission denied while trying to connect to the Docker API
at unix:///var/run/docker.sock
```

The active user does not currently have permission to access the Docker
socket. Because of this, the following could not be performed:

- `docker exec`
- `docker inspect`
- `docker build`
- `docker stop`
- `docker rm`

The container filesystem could not be inspected directly for the same reason.

## Protected Artifact Hashes

The Qwen base model and LoRA adapter remain unchanged.

```text
Qwen model:
f47f71177f32bcd101b7573ec9171e6a57f4d31148d38e382306f42996874b

LoRA adapter:
844fc15b4c4126e814f357de8d5941d144fb0f6bc8c7853eb4def260f0549287
```

## Required Fix

No additional source-code change is required. Rebuild the image and recreate
only the `followupfinder-ai` container after Docker permissions are fixed:

```bash
cd /home/ak/Downloads/followupfinder-ai\(1\)/followupfinder

docker build \
  -f ai/Dockerfile \
  -t followupfinder-ai:cpu \
  ai

docker stop followupfinder-ai
docker rm followupfinder-ai

docker run -d \
  --name followupfinder-ai \
  -p 8001:8000 \
  -e FOLLOWUPFINDER_DEVICE=cpu \
  -e FOLLOWUPFINDER_BASE_MODEL_PATH=/models/Qwen3-0.6B \
  -e FOLLOWUPFINDER_ADAPTER_PATH=/models/lora-round3 \
  -v "$PWD/ai/inference/models/Qwen3-0.6B:/models/Qwen3-0.6B:ro" \
  -v "$PWD/ai/adapters/lora_round3_gpu:/models/lora-round3:ro" \
  followupfinder-ai:cpu
```

Then verify:

```bash
curl -s http://localhost:8001/health

curl -s -X POST http://localhost:8001/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Ramesh ke saath meeting kal 3 baje scheduled hai."}'
```

## Expected Correct Response

```json
{
  "contact": {
    "name": "Ramesh",
    "organization": null
  },
  "event": {
    "type": "meeting",
    "description": null,
    "amount": null,
    "currency": null,
    "status": "planned"
  },
  "followup": {
    "required": false,
    "action": null,
    "date_expression": "kal 3 baje"
  }
}
```

## Safety Confirmations

- Qwen weights were not modified.
- LoRA adapter weights were not modified.
- No retraining was performed.
- No datasets were deleted.
- No evaluation results were deleted.
- No unrelated containers or services were changed.
- The API contract remains unchanged.
