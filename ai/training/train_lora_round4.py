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

MODEL_NAME = "./ai/inference/models/Qwen3-0.6B"

# Round 3 combined training dataset
TRAIN_FILE = "ai/datasets/train_round3_combined.jsonl"

# Round 3 validation dataset
VALIDATION_FILE = "ai/datasets/val_round3.jsonl"

# New Round 3 adapter output
OUTPUT_DIR = "./ai/adapters/lora_round4_gpu"

MAX_LENGTH = 512


# ==================================================
# GPU CHECK
# ==================================================

if not torch.cuda.is_available():
    raise RuntimeError("CUDA GPU not available!")

device = torch.device("cuda")

print("========================================")
print("ROUND 3 GPU ENVIRONMENT")
print("========================================")
print("GPU:", torch.cuda.get_device_name(0))
print("CUDA:", torch.version.cuda)
print("PyTorch:", torch.__version__)
print("BF16 supported:", torch.cuda.is_bf16_supported())
print("========================================")


# ==================================================
# LOAD JSONL
# ==================================================

def load_jsonl(path):

    examples = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            if line.strip():
                examples.append(
                    json.loads(line)
                )

    return examples


train_examples = load_jsonl(
    TRAIN_FILE
)

validation_examples = load_jsonl(
    VALIDATION_FILE
)


print(
    f"\nTraining examples: {len(train_examples)}"
)

print(
    f"Validation examples: {len(validation_examples)}"
)


# ==================================================
# DATASET
# ==================================================

train_dataset = Dataset.from_list(
    train_examples
)

validation_dataset = Dataset.from_list(
    validation_examples
)


# ==================================================
# TOKENIZER
# ==================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ==================================================
# TOKENIZATION
# ==================================================

def tokenize_example(example):

    messages = example["messages"]


    # ----------------------------------------------
    # Complete conversation
    # ----------------------------------------------

    full_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )


    # ----------------------------------------------
    # User-only prompt
    #
    # We use this to determine where the assistant
    # response begins.
    # ----------------------------------------------

    prompt_text = tokenizer.apply_chat_template(
        [messages[0]],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )


    # ----------------------------------------------
    # Tokenize complete conversation
    # ----------------------------------------------

    full_ids = tokenizer(
        full_text,
        add_special_tokens=False,
        truncation=True,
        max_length=MAX_LENGTH,
    )["input_ids"]


    # ----------------------------------------------
    # Tokenize user prompt
    # ----------------------------------------------

    prompt_ids = tokenizer(
        prompt_text,
        add_special_tokens=False,
    )["input_ids"]


    # ----------------------------------------------
    # Determine assistant start
    # ----------------------------------------------

    prompt_length = min(
        len(prompt_ids),
        len(full_ids),
    )


    # ----------------------------------------------
    # Create labels
    # ----------------------------------------------

    labels = full_ids.copy()


    # Don't calculate loss on the user's message.
    #
    # -100 tells PyTorch/Transformers:
    # "ignore this token when calculating loss."
    #

    for i in range(prompt_length):

        labels[i] = -100


    return {
        "input_ids": full_ids,

        "attention_mask": [
            1
            for _ in full_ids
        ],

        "labels": labels,
    }


# ==================================================
# TOKENIZE TRAINING DATA
# ==================================================

print(
    "\nTokenizing training dataset..."
)

train_dataset = train_dataset.map(
    tokenize_example,
    remove_columns=train_dataset.column_names,
)


# ==================================================
# TOKENIZE VALIDATION DATA
# ==================================================

print(
    "\nTokenizing validation dataset..."
)

validation_dataset = validation_dataset.map(
    tokenize_example,
    remove_columns=validation_dataset.column_names,
)


# ==================================================
# MODEL
# ==================================================

print(
    "\nLoading Qwen3-0.6B in BF16..."
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    local_files_only=True,
    dtype=torch.bfloat16,
)

model.config.use_cache = False

model = model.to(device)


# ==================================================
# LoRA CONFIGURATION
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


# ==================================================
# APPLY LoRA
# ==================================================

model = get_peft_model(
    model,
    lora_config,
)


# ==================================================
# TRAINABLE PARAMETERS
# ==================================================

print(
    "\nLoRA parameter information:"
)

model.print_trainable_parameters()


# ==================================================
# TRAINING ARGUMENTS
# ==================================================

training_args = TrainingArguments(

    output_dir=OUTPUT_DIR,


    # ----------------------------------------------
    # Training duration
    # ----------------------------------------------

    num_train_epochs=3,
    gradient_accumulation_steps=1,


    # ----------------------------------------------
    # Batch
    # ----------------------------------------------

    per_device_train_batch_size=1,
    gradient_checkpointing=True,

    per_device_eval_batch_size=1,


    # ----------------------------------------------
    # Learning
    # ----------------------------------------------

    learning_rate=2e-4,


    # ----------------------------------------------
    # Logging
    # ----------------------------------------------

    logging_steps=50,


    # ----------------------------------------------
    # Evaluation
    # ----------------------------------------------

    eval_strategy="epoch",


    # ----------------------------------------------
    # Checkpoints
    # ----------------------------------------------

    save_strategy="epoch",

    save_total_limit=1,


    # ----------------------------------------------
    # Precision
    # ----------------------------------------------

    bf16=True,

    fp16=False,


    # ----------------------------------------------
    # GPU
    # ----------------------------------------------

    use_cpu=False,

    dataloader_num_workers=0,


    # ----------------------------------------------
    # Reproducibility
    # ----------------------------------------------

    seed=42,


    # ----------------------------------------------
    # Disable external logging
    # ----------------------------------------------

    report_to="none",
)


# ==================================================
# TRAINER
# ==================================================

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=validation_dataset,

    processing_class=tokenizer,
)


# ==================================================
# TRAINING INFORMATION
# ==================================================

print("\n========================================")
print("STARTING ROUND 3 LORA TRAINING")
print("========================================")

print(
    "Model: Qwen/Qwen3-0.6B"
)

print(
    "Training dataset: 5,200 examples"
)

print(
    "Validation dataset: 400 examples"
)

print(
    "Epochs: 1"
)

print(
    "LoRA: r=8, alpha=16"
)

print(
    "LoRA dropout: 0.05"
)

print(
    "Target modules: q/k/v/o"
)

print(
    "Learning rate: 2e-4"
)

print(
    "Max length: 512"
)

print(
    "Precision: BF16"
)

print(
    "Seed: 42"
)

print(
    "Output:",
    OUTPUT_DIR
)

print("========================================\n")


# ==================================================
# TRAIN
# ==================================================

trainer.train()


# ==================================================
# SAVE ADAPTER
# ==================================================

print(
    "\nSaving Round 3 LoRA adapter..."
)

trainer.save_model(
    OUTPUT_DIR
)

tokenizer.save_pretrained(
    OUTPUT_DIR
)


# ==================================================
# COMPLETE
# ==================================================

print("\n========================================")
print("ROUND 3 GPU TRAINING COMPLETE")
print("========================================")

print(
    f"Adapter saved to: {OUTPUT_DIR}"
)

print("========================================")