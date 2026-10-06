import json
import re

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

from peft import PeftModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "./ai/inference/models/Qwen3-0.6B"
LORA_PATH = "./ai/adapters/lora_round3_gpu"
TEST_PATH = "ai/datasets/test_round3.jsonl"
OUTPUT_PATH = "ai/datasets/lora_round3_results.jsonl"

MAX_NEW_TOKENS = 300


# ============================================================
# GPU CHECK
# ============================================================

print("=" * 60)
print("ROUND 3 LORA EVALUATION")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError(
        "CUDA GPU is not available."
    )

print("CUDA version:", torch.version.cuda)
print("GPU:", torch.cuda.get_device_name(0))

print(
    "VRAM:",
    round(
        torch.cuda.get_device_properties(0).total_memory
        / 1024**3,
        2,
    ),
    "GB",
)

print(
    "BF16 supported:",
    torch.cuda.is_bf16_supported()
)

print("=" * 60)


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

test_examples = []

with open(
    TEST_PATH,
    "r",
    encoding="utf-8",
) as f:

    for line in f:

        if line.strip():

            test_examples.append(
                json.loads(line)
            )

print(
    "Examples evaluated:",
    len(test_examples)
)


# ============================================================
# LOAD TOKENIZER
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded.")


# ============================================================
# LOAD BASE MODEL
# ============================================================

print("\nLoading base model in BF16...")

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
    dtype=torch.bfloat16,
)

base_model = base_model.to("cuda")

base_model.config.use_cache = True

print("Base model loaded.")


# ============================================================
# LOAD ROUND 3 LoRA
# ============================================================

print("\nLoading Round 3 LoRA adapter...")

model = PeftModel.from_pretrained(
    base_model,
    LORA_PATH,
)

model = model.to("cuda")

model.eval()

print("Round 3 adapter loaded.")


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    text = text.strip()

    # Remove Qwen thinking if it appears.
    if "</think>" in text:

        text = text.split(
            "</think>",
            1
        )[1].strip()

    # Remove markdown code fences.
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"```\s*",
        "",
        text,
    )

    # Find first JSON object.
    start = text.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for i in range(
        start,
        len(text),
    ):

        char = text[i]

        if escaped:

            escaped = False
            continue

        if char == "\\" and in_string:

            escaped = True
            continue

        if char == '"':

            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":

            depth += 1

        elif char == "}":

            depth -= 1

            if depth == 0:

                candidate = text[
                    start:i + 1
                ]

                try:

                    return json.loads(
                        candidate
                    )

                except json.JSONDecodeError:

                    return None

    return None


# ============================================================
# FIELD ACCESS
# ============================================================

FIELDS = [
    "contact.name",
    "contact.organization",
    "event.type",
    "event.description",
    "event.amount",
    "event.currency",
    "event.status",
    "followup.required",
    "followup.action",
    "followup.date_expression",
]


def get_field(obj, path):

    current = obj

    for key in path.split("."):

        if not isinstance(
            current,
            dict,
        ):

            return None

        current = current.get(key)

    return current


# ============================================================
# EVALUATION
# ============================================================

field_correct = {
    field: 0
    for field in FIELDS
}

json_success = 0
exact_matches = 0

results = []


print("\nStarting evaluation...")
print("=" * 60)


for index, example in enumerate(
    test_examples,
    1,
):

    messages = example["messages"]

    user_message = messages[0]["content"]

    expected = json.loads(
        messages[1]["content"]
    )


    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt_messages = [
        messages[0]
    ]

    prompt = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )


    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    inputs = {
        key: value.to("cuda")
        for key, value in inputs.items()
    }


    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    with torch.no_grad():

        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )


    # --------------------------------------------------------
    # Only decode newly generated tokens
    # --------------------------------------------------------

    generated_ids = output_ids[
        0,
        inputs["input_ids"].shape[1]:,
    ]

    generated_text = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True,
    ).strip()


    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    predicted = extract_json(
        generated_text
    )


    if predicted is not None:

        json_success += 1


        # ----------------------------------------------
        # Field accuracy
        # ----------------------------------------------

        for field in FIELDS:

            expected_value = get_field(
                expected,
                field,
            )

            predicted_value = get_field(
                predicted,
                field,
            )

            if (
                predicted_value
                == expected_value
            ):

                field_correct[field] += 1


        # ----------------------------------------------
        # Exact match
        # ----------------------------------------------

        if predicted == expected:

            exact_matches += 1


    # --------------------------------------------------------
    # Save detailed result
    # --------------------------------------------------------

    results.append(
        {
            "index": index,
            "input": user_message,
            "expected": expected,
            "predicted": predicted,
            "raw_output": generated_text,
            "exact_match": (
                predicted == expected
                if predicted is not None
                else False
            ),
        }
    )


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if index % 25 == 0:

        print(
            f"Evaluated {index}/{len(test_examples)}"
        )


# ============================================================
# SAVE RESULTS
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8",
) as f:

    for result in results:

        f.write(
            json.dumps(
                result,
                ensure_ascii=False,
            )
            + "\n"
        )


# ============================================================
# FINAL REPORT
# ============================================================

total = len(test_examples)

print("\n")
print("=" * 60)
print("LORA ROUND 3 EVALUATION REPORT")
print("=" * 60)

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

for field in FIELDS:

    correct = field_correct[field]

    print(
        f"  {field}: "
        f"{correct}/{total} "
        f"({correct / total * 100:.2f}%)"
    )


print(
    f"\nDetailed results saved to: "
    f"{OUTPUT_PATH}"
)

print("\n")
print("=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)