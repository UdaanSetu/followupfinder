import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)

from datasets import load_dataset

from peft import (
    LoraConfig,
    get_peft_model,
)


# ============================================================
# 1. Configuration
# ============================================================

MODEL_NAME = "Qwen/Qwen3-0.6B"

DATA_PATH = "ai/datasets/train_smoke.jsonl"

OUTPUT_DIR = "./ai/adapters/lora_gpu_smoke"

MAX_LENGTH = 512


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
print("VRAM:",
      round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
      "GB")
print("BF16 supported:", torch.cuda.is_bf16_supported())

print("=" * 60)


# ============================================================
# 3. Load tokenizer
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Tokenizer loaded successfully.")


# ============================================================
# 4. Load model
# ============================================================

print("\nLoading model in BF16...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16,
)

model = model.to("cuda")

print("Model loaded successfully.")

total_parameters = sum(
    parameter.numel()
    for parameter in model.parameters()
)

print(f"Base parameters: {total_parameters:,}")


# ============================================================
# 5. Add LoRA
# ============================================================

print("\nAdding LoRA adapter...")

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,

    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],

    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(
    model,
    lora_config
)

print("LoRA adapter added.")

model.print_trainable_parameters()


# ============================================================
# 6. Load dataset
# ============================================================

print("\nLoading training dataset...")

dataset = load_dataset(
    "json",
    data_files=DATA_PATH,
    split="train"
)

print("Training examples:", len(dataset))


# ============================================================
# 7. Format conversations
# ============================================================

def format_example(example):

    messages = example["messages"]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )

    return {
        "text": text
    }


print("\nFormatting dataset...")

formatted_dataset = dataset.map(
    format_example
)

print("Formatting complete.")


# ============================================================
# 8. Tokenize + assistant-only labels
# ============================================================

def tokenize_example(example):

    messages = example["messages"]

    # --------------------------------------------------------
    # User portion
    # --------------------------------------------------------

    user_text = tokenizer.apply_chat_template(
        [messages[0]],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    user_tokens = tokenizer(
        user_text,
        add_special_tokens=False,
    )

    # --------------------------------------------------------
    # Complete conversation
    # --------------------------------------------------------

    full_tokens = tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        add_special_tokens=False,
    )

    input_ids = full_tokens["input_ids"]
    attention_mask = full_tokens["attention_mask"]

    # --------------------------------------------------------
    # Mask user tokens
    # --------------------------------------------------------

    user_length = len(user_tokens["input_ids"])

    labels = [-100] * len(input_ids)

    # --------------------------------------------------------
    # Train only on assistant response
    # --------------------------------------------------------

    for i in range(user_length, len(input_ids)):
        labels[i] = input_ids[i]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


print("\nTokenizing dataset...")

tokenized_dataset = formatted_dataset.map(
    tokenize_example,
    remove_columns=formatted_dataset.column_names
)

print("Tokenization complete.")


# ============================================================
# 9. Data collator
# ============================================================

print("\nCreating data collator...")

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True,
    label_pad_token_id=-100,
)

print("Data collator ready.")


# ============================================================
# 10. Training configuration
# ============================================================

print("\nCreating training configuration...")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    # Smoke test
    num_train_epochs=1,

    # Start conservatively
    per_device_train_batch_size=1,

    gradient_accumulation_steps=1,

    learning_rate=2e-4,

    logging_steps=10,

    save_strategy="epoch",

    # GPU
    use_cpu=False,

    # RTX 5070 supports BF16
    bf16=True,
    fp16=False,

    # Don't remove columns automatically
    remove_unused_columns=False,

    # Disable external reporting
    report_to="none",
)

print("Training configuration ready.")


# ============================================================
# 11. Create Trainer
# ============================================================

print("\nCreating Trainer...")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

print("Trainer created successfully.")


# ============================================================
# 12. Start training
# ============================================================

print("\n========================================")
print("STARTING GPU LORA TRAINING")
print("========================================")

print(f"Examples: {len(tokenized_dataset)}")
print("Epochs: 1")
print("Batch size: 1")
print("Learning rate: 2e-4")
print("Device: CUDA")
print("Precision: BF16")
print("GPU:", torch.cuda.get_device_name(0))

print("========================================\n")

train_result = trainer.train()


# ============================================================
# 13. Save LoRA adapter
# ============================================================

print("\n========================================")
print("TRAINING COMPLETE")
print("========================================")

print("Saving LoRA adapter...")

trainer.save_model(OUTPUT_DIR)

tokenizer.save_pretrained(OUTPUT_DIR)

print(f"LoRA adapter saved to: {OUTPUT_DIR}")

print("\nTraining statistics:")

print(train_result.metrics)

print("\n========================================")
print("DONE")
print("========================================")