# FollowUpFinder AI

## Model and adapter

Inference uses the local Qwen3-0.6B base model with the trained round-three
LoRA adapter:

- Base model: `ai/inference/models/Qwen3-0.6B/`
- Production adapter: `ai/adapters/lora_round3_gpu/`

The Qwen base model is intentionally not stored in Git because it is a large
model asset. Obtain Qwen3-0.6B from its approved Hugging Face source, or place
the existing local model files at the path above. The adapter weights are
preserved and are not converted or retrained.

## Inference API

The backend can use the single public function:

```python
from ai.inference import extract_followup

result = extract_followup("Rahul ko 50k ka website quotation bhej diya, Friday ko call karna hai.")
```

The loader initializes the tokenizer, Qwen model, and LoRA adapter once using a
cached singleton. Each request then applies the production prompt contract and
the adapter-compatible Qwen chat template, tokenizes, generates
deterministically, and parses the JSON response. The round-three adapter was
trained with user-only messages, so inference preserves that format rather
than adding an untrained system-role message.

Expected output:

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

Missing information remains `null`; relative date expressions remain unchanged.
Parsing failures raise `InferenceParseError` for the backend to handle.

## Local inference

Run from the repository root with the existing Python environment:

```bash
python -c 'from ai.inference import extract_followup; print(extract_followup("Ramesh se meeting kal schedule hai."))'
```

Set `FOLLOWUPFINDER_DEVICE=cpu` to force CPU inference. Without that setting,
CUDA is used when available and CPU is used otherwise.

## Training

Training remains separate from production inference. Existing training scripts
are preserved under `ai/training/`, and datasets remain under `ai/datasets/`.
Do not run training as part of backend startup or request handling. The
training scripts retain the existing LoRA configuration, dataset loading,
tokenizer setup, assistant-only masking, evaluation settings, and
reproducibility behavior.

## Architectural boundary

The AI component performs language understanding only:

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

AI inference does not connect to MongoDB, resolve database IDs or calendar
dates, create records, send reminders, make business decisions, or call
external APIs.
