"""Load and cache the local Qwen base model with the production LoRA adapter."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_MODEL_PATH = PROJECT_ROOT / "ai" / "inference" / "models" / "Qwen3-0.6B"
DEFAULT_ADAPTER_PATH = PROJECT_ROOT / "ai" / "adapters" / "lora_round3_gpu"


def _device() -> torch.device:
    requested = os.getenv("FOLLOWUPFINDER_DEVICE")
    if requested:
        return torch.device(requested)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def load_model() -> tuple[Any, Any, torch.device]:
    """Load tokenizer and model once, then reuse them for all requests."""
    base_model_path = Path(os.getenv("FOLLOWUPFINDER_BASE_MODEL_PATH", DEFAULT_BASE_MODEL_PATH))
    adapter_path = Path(os.getenv("FOLLOWUPFINDER_ADAPTER_PATH", DEFAULT_ADAPTER_PATH))

    if not base_model_path.is_dir():
        raise FileNotFoundError(f"Base model directory not found: {base_model_path}")
    if not adapter_path.is_dir():
        raise FileNotFoundError(f"LoRA adapter directory not found: {adapter_path}")

    device = _device()
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        local_files_only=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        local_files_only=True,
        torch_dtype=dtype,
    )
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.to(device)
    model.eval()
    return tokenizer, model, device
