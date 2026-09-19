import json
import torch

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model


# ==================================================
# Configuration
# ==================================================

MODEL_NAME = "Qwen/Qwen3-0.6B"

TRAIN_FILE = "ai/datasets/train.jsonl"
VALIDATION_FILE = "ai/datasets/validation.jsonl"

OUTPUT_DIR = "./ai/adapters/lora_full_gpu"

MAX_LENGTH = 512


# ==================================================
# GPU check
# ==================================================

if not torch.cuda.is_available():
    raise RuntimeError("CUDA GPU not available!")

device = torch.device("cuda")

print("========================================")
print("GPU ENVIRONMENT")
print("========================================")
print("GPU:", torch.cuda.get_device_name(0))
print("CUDA:", torch.version.cuda)
print("BF16 supported:", torch.cuda.is_bf16_supported())
print("========================================")


# ==================================================
# Load JSONL
# ==================================================

def load_jsonl(path):
    examples = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    return examples


train_examples = load_jsonl(TRAIN_FILE)
validation_examples = load_jsonl(VALIDATION_FILE)

print(f"\nTraining examples: {len(train_examples)}")
print(f"Validation examples: {len(validation_examples)}")


# ==================================================
# Dataset
# ==================================================

train_dataset = Dataset.from_list(train_examples)
validation_dataset = Dataset.from_list(validation_examples)


# ==================================================
# Tokenizer
# ==================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ==================================================
# Tokenization
# ==================================================

def tokenize_example(example):

    messages = example["messages"]

    # Complete conversation
    full_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )

    # User-only portion
    prompt_text = tokenizer.apply_chat_template(
        [messages[0]],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    full_ids = tokenizer(
        full_text,
        add_special_tokens=False,
        truncation=True,
        max_length=MAX_LENGTH,
    )["input_ids"]

    prompt_ids = tokenizer(
        prompt_text,
        add_special_tokens=False,
    )["input_ids"]

    prompt_length = min(
        len(prompt_ids),
        len(full_ids),
    )

    labels = full_ids.copy()

    # Don't calculate loss on user's message.
    for i in range(prompt_length):
        labels[i] = -100

    return {
        "input_ids": full_ids,
        "attention_mask": [1] * len(full_ids),
        "labels": labels,
    }


print("\nTokenizing training dataset...")

train_dataset = train_dataset.map(
    tokenize_example,
    remove_columns=train_dataset.column_names,
)

print("\nTokenizing validation dataset...")

validation_dataset = validation_dataset.map(
    tokenize_example,
    remove_columns=validation_dataset.column_names,
)


# ==================================================
# Model
# ==================================================

print("\nLoading Qwen3-0.6B in BF16...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
    dtype=torch.bfloat16,
)

model.config.use_cache = False

model = model.to(device)


# ==================================================
# LoRA
# ==================================================

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)

model = get_peft_model(
    model,
    lora_config,
)

model.print_trainable_parameters()


# ==================================================
# Training arguments
# ==================================================

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    num_train_epochs=1,

    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,

    learning_rate=2e-4,

    logging_steps=50,

    eval_strategy="epoch",

    save_strategy="epoch",
    save_total_limit=1,

    report_to="none",

    bf16=True,
    fp16=False,

    use_cpu=False,

    dataloader_num_workers=0,

    seed=42,
)


# ==================================================
# Trainer
# ==================================================

trainer = Trainer(
    model=model,
    args=training_args,

    train_dataset=train_dataset,
    eval_dataset=validation_dataset,

    processing_class=tokenizer,
)


# ==================================================
# Train
# ==================================================

print("\n========================================")
print("STARTING FULL GPU TRAINING")
print("========================================")
print("Dataset: 4,000 training examples")
print("Validation: 500 examples")
print("Epochs: 1")
print("LoRA: r=8, alpha=16")
print("Learning rate: 2e-4")
print("Precision: BF16")
print("========================================\n")


trainer.train()


# ==================================================
# Save
# ==================================================

print("\nSaving GPU LoRA adapter...")

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n========================================")
print("GPU TRAINING COMPLETE")
print("========================================")

print(f"Adapter saved to: {OUTPUT_DIR}")