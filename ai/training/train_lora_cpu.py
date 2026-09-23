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

MODEL_PATH = (
    "/home/ak/.cache/huggingface/hub/"
    "models--Qwen--Qwen3-0.6B/snapshots/"
    "c1899de289a04d12100db370d81485cdf75e47ca"
)

DATA_PATH = "ai/datasets/train_smoke.jsonl"

OUTPUT_DIR = "./ai/adapters/lora_smoke"

MAX_LENGTH = 512


# ============================================================
# 2. Load tokenizer
# ============================================================

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

print("Tokenizer loaded successfully.")


# ============================================================
# 3. Load model
# ============================================================

print("Loading model...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    dtype=torch.float32
)

print("Model loaded successfully.")

total_parameters = sum(
    parameter.numel()
    for parameter in model.parameters()
)

print(f"Base parameters: {total_parameters:,}")


# ============================================================
# 4. Add LoRA
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
# 5. Load dataset
# ============================================================

print("\nLoading training dataset...")

dataset = load_dataset(
    "json",
    data_files=DATA_PATH,
    split="train"
)

print("Training examples:", len(dataset))


# ============================================================
# 6. Format conversations
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
# 7. Tokenize + assistant-only labels
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
# 8. Data collator
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
# 9. Training configuration
# ============================================================

print("\nCreating training configuration...")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    # First smoke test
    num_train_epochs=1,

    # Your laptop has limited RAM
    per_device_train_batch_size=1,

    # No gradient accumulation for this first test
    gradient_accumulation_steps=1,

    # Small learning rate for LoRA
    learning_rate=2e-4,

    # Log training progress
    logging_steps=10,

    # Save at the end
    save_strategy="epoch",

    # CPU
    use_cpu=True,

    # Don't remove columns automatically
    remove_unused_columns=False,

    # Disable external reporting
    report_to="none",

    # Keep training simple
    fp16=False,
    bf16=False,
)

print("Training configuration ready.")


# ============================================================
# 10. Create Trainer
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
# 11. Start training
# ============================================================

print("\n========================================")
print("STARTING LORA TRAINING")
print("========================================")

print(f"Examples: {len(tokenized_dataset)}")
print("Epochs: 1")
print("Batch size: 1")
print("Learning rate: 2e-4")
print("Device: CPU")

print("========================================\n")

train_result = trainer.train()


# ============================================================
# 12. Save LoRA adapter
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