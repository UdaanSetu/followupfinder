"""Production FollowUpFinder inference entry point."""

from __future__ import annotations

import torch

from .model_loader import load_model
from .parser import parse_model_output
from .prompt import build_messages
from .grounding import ground_result

MAX_NEW_TOKENS = 300


def extract_followup(text: str) -> dict:
    """Extract structured follow-up information from natural-language text."""
    tokenizer, model, device = load_model()
    prompt = tokenizer.apply_chat_template(
        build_messages(text),
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_ids = output_ids[0, inputs["input_ids"].shape[1] :]
    generated_text = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True,
    ).strip()
    return ground_result(text, parse_model_output(generated_text))
