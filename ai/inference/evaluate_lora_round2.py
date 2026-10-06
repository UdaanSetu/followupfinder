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

MODEL_NAME = "Qwen/Qwen3-0.6B"

LORA_PATH = "./ai/adapters/lora_round2_gpu"
TEST_PATH = "ai/datasets/test.jsonl"

MAX_NEW_TOKENS = 300


# ============================================================
# 2. GPU check
# ============================================================

print("=" * 60)
print("GPU ENVIRONMENT")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("CUDA GPU is not available.")

print("CUDA version:", torch.version.cuda)
print("GPU:", torch.cuda.get_device_name(0))

print(
    "VRAM:",
    round(
        torch.cuda.get_device_properties(0).total_memory / 1024**3,
        2
    ),
    "GB"
)

print(
    "BF16 supported:",
    torch.cuda.is_bf16_supported()
)

print("=" * 60)


# ============================================================
# 3. Load tokenizer
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Tokenizer loaded.")


# ============================================================
# 4. Load base model
# ============================================================

print("\nLoading base model in BF16...")

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16,
)

base_model = base_model.to("cuda")

print("Base model loaded.")


# ============================================================
# 5. Load LoRA adapter
# ============================================================

print("\nLoading LoRA adapter...")

model = PeftModel.from_pretrained(
    base_model,
    LORA_PATH
)

model = model.to("cuda")

model.eval()

print("LoRA model loaded.")


# ============================================================
# 6. Load test dataset
# ============================================================

print("\nLoading test dataset...")

test_examples = []

with open(
    TEST_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if line.strip():

            test_examples.append(
                json.loads(line)
            )

print("Test examples:", len(test_examples))


# ============================================================
# 7. Generate prediction
# ============================================================

def generate_prediction(messages):

    prompt = tokenizer.apply_chat_template(
        [messages[0]],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {
        key: value.to("cuda")
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
        )

    generated_tokens = outputs[
        0
    ][
        inputs["input_ids"].shape[1]:
    ]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    return response.strip()


# ============================================================
# 8. Extract JSON from model response
# ============================================================

def extract_json(text):

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # --------------------------------------------------------
    # Try direct JSON parsing
    # --------------------------------------------------------

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        pass

    # --------------------------------------------------------
    # Try finding JSON object inside response
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = text[
            start:end + 1
        ]

        try:

            return json.loads(candidate)

        except json.JSONDecodeError:

            return None

    return None


# ============================================================
# 9. Helper for nested fields
# ============================================================

def get_field(data, path):

    current = data

    for key in path:

        if not isinstance(current, dict):

            return None

        current = current.get(key)

    return current


# ============================================================
# 10. Evaluation
# ============================================================

print("\n========================================")
print("STARTING LORA EVALUATION")
print("========================================")

print(
    "Test examples:",
    len(test_examples)
)

print(
    "Device:",
    torch.cuda.get_device_name(0)
)

print("Precision: BF16")

print("========================================\n")


results = []

total = len(test_examples)

json_success = 0

exact_matches = 0


# ------------------------------------------------------------
# Fields we want to evaluate
# ------------------------------------------------------------

field_paths = [

    (
        "contact.name",
        ["contact", "name"]
    ),

    (
        "contact.organization",
        ["contact", "organization"]
    ),

    (
        "event.type",
        ["event", "type"]
    ),

    (
        "event.description",
        ["event", "description"]
    ),

    (
        "event.amount",
        ["event", "amount"]
    ),

    (
        "event.currency",
        ["event", "currency"]
    ),

    (
        "event.status",
        ["event", "status"]
    ),

    (
        "followup.required",
        ["followup", "required"]
    ),

    (
        "followup.action",
        ["followup", "action"]
    ),

    (
        "followup.date_expression",
        ["followup", "date_expression"]
    ),
]


field_correct = {
    name: 0
    for name, _ in field_paths
}


# ============================================================
# Evaluate every test example
# ============================================================

for index, example in enumerate(
    test_examples,
    start=1
):

    messages = example["messages"]

    # --------------------------------------------------------
    # IMPORTANT:
    # Our dataset stores the expected JSON inside
    # the assistant message.
    #
    # messages[0] = user input
    # messages[1] = expected assistant JSON
    # --------------------------------------------------------

    expected_text = messages[1]["content"]

    expected = json.loads(
        expected_text
    )

    # --------------------------------------------------------
    # Generate model prediction
    # --------------------------------------------------------

    prediction_text = generate_prediction(
        messages
    )

    prediction = extract_json(
        prediction_text
    )

    # --------------------------------------------------------
    # JSON parse success
    # --------------------------------------------------------

    if prediction is not None:

        json_success += 1

    else:

        prediction = {}

    # --------------------------------------------------------
    # Field comparison
    # --------------------------------------------------------

    for field_name, path in field_paths:

        expected_value = get_field(
            expected,
            path
        )

        predicted_value = get_field(
            prediction,
            path
        )

        if predicted_value == expected_value:

            field_correct[field_name] += 1

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    is_exact_match = (
        prediction == expected
    )

    if is_exact_match:

        exact_matches += 1

    # --------------------------------------------------------
    # Store detailed result
    # --------------------------------------------------------

    result = {

        "index": index,

        "input": messages,

        "expected": expected,

        "prediction_text": prediction_text,

        "prediction": prediction,

        "exact_match": is_exact_match,

    }

    results.append(result)

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if index % 10 == 0:

        print(
            f"Evaluated {index}/{total}"
        )


# ============================================================
# 11. Evaluation report
# ============================================================

print("\n========================================")
print("EVALUATION REPORT")
print("========================================")

print(
    f"Examples evaluated: "
    f"{total}"
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
    "ai/datasets/lora_full_gpu_results.jsonl"
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