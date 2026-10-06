import json
import re

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

from peft import PeftModel


# ============================================================
# 1. Configuration
# ============================================================

MODEL_PATH = (
    "/home/ak/.cache/huggingface/hub/"
    "models--Qwen--Qwen3-0.6B/snapshots/"
    "c1899de289a04d12100db370d81485cdf75e47ca"
)

LORA_PATH = "./ai/adapters/lora_smoke"
TEST_PATH = "ai/datasets/test.jsonl"

MAX_NEW_TOKENS = 300


# ============================================================
# 2. Load tokenizer
# ============================================================

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

print("Tokenizer loaded.")


# ============================================================
# 3. Load base model
# ============================================================

print("Loading base model...")

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    dtype=torch.float32
)

print("Base model loaded.")


# ============================================================
# 4. Load LoRA adapter
# ============================================================

print("\nLoading LoRA adapter...")

model = PeftModel.from_pretrained(
    base_model,
    LORA_PATH
)

model.eval()

print("LoRA model loaded.")


# ============================================================
# 5. Load test dataset
# ============================================================

print("\nLoading test dataset...")

test_examples = []

with open(
    TEST_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:
        test_examples.append(
            json.loads(line)
        )

print(f"Test examples: {len(test_examples)}")


# ============================================================
# 6. JSON extraction helper
# ============================================================

def extract_json(text):

    # Remove markdown code fences
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    # Find the first JSON object
    start = text.find("{")

    if start == -1:
        return None

    # Try progressively shorter endings
    for end in range(
        len(text),
        start,
        -1
    ):

        candidate = text[start:end].strip()

        try:
            return json.loads(candidate)

        except json.JSONDecodeError:
            continue

    return None


# ============================================================
# 7. Get expected answer
# ============================================================

def get_expected(example):

    for message in example["messages"]:

        if message["role"] == "assistant":

            return json.loads(
                message["content"]
            )

    return None


# ============================================================
# 8. Generate model response
# ============================================================

def generate_response(user_message):

    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Only decode newly generated tokens
    generated_tokens = outputs[
        0,
        inputs["input_ids"].shape[1]:
    ]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=False
    )


# ============================================================
# 9. Compare nested fields
# ============================================================

FIELDS = [
    ("contact", "name"),
    ("contact", "organization"),
    ("event", "type"),
    ("event", "description"),
    ("event", "amount"),
    ("event", "currency"),
    ("event", "status"),
    ("followup", "required"),
    ("followup", "action"),
    ("followup", "date_expression"),
]


def get_field(data, section, field):

    if not isinstance(data, dict):
        return None

    section_data = data.get(section)

    if not isinstance(section_data, dict):
        return None

    return section_data.get(field)


# ============================================================
# 10. Evaluation
# ============================================================

field_correct = {
    f"{section}.{field}": 0
    for section, field in FIELDS
}

exact_matches = 0
json_success = 0

results = []


print("\n========================================")
print("STARTING LORA EVALUATION")
print("========================================")

for index, example in enumerate(test_examples):

    user_message = example["messages"][0]["content"]

    expected = get_expected(example)

    print(
        f"\nEvaluating {index + 1}/{len(test_examples)}"
    )

    generated_text = generate_response(
        user_message
    )

    predicted = extract_json(
        generated_text
    )

    if predicted is not None:

        json_success += 1

    is_exact = (
        predicted == expected
    )

    if is_exact:
        exact_matches += 1

    for section, field in FIELDS:

        key = f"{section}.{field}"

        predicted_value = get_field(
            predicted,
            section,
            field
        )

        expected_value = get_field(
            expected,
            section,
            field
        )

        if predicted_value == expected_value:

            field_correct[key] += 1

    results.append({
        "input": user_message,
        "expected": expected,
        "prediction": predicted,
        "raw_output": generated_text,
        "exact_match": is_exact,
    })


# ============================================================
# 11. Print report
# ============================================================

total = len(test_examples)

print("\n\n========================================")
print("LORA EVALUATION REPORT")
print("========================================")

print(
    f"Examples evaluated: {total}"
)

print(
    f"JSON parse success: "
    f"{json_success}/{total} "
    f"({json_success / total * 100:.2f}%)"
)

print(
    f"Exact matches: "
    f"{exact_matches}/{total} "
    f"({exact_matches / total * 100:.2f}%)"
)

print(
    f"Mismatches: "
    f"{total - exact_matches}"
)

print("\nField accuracy:")

for key, correct in field_correct.items():

    print(
        f"  {key}: "
        f"{correct}/{total} "
        f"({correct / total * 100:.2f}%)"
    )


# ============================================================
# 12. Save detailed results
# ============================================================

OUTPUT_PATH = (
    "ai/datasets/lora_smoke_results.jsonl"
)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    for result in results:

        file.write(
            json.dumps(
                result,
                ensure_ascii=False
            )
            + "\n"
        )

print(
    f"\nDetailed results saved to: "
    f"{OUTPUT_PATH}"
)

print("\n========================================")
print("EVALUATION COMPLETE")
print("========================================")