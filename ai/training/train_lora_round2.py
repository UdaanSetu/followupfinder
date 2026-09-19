import torch

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)

from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
)


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "Qwen/Qwen3-0.6B"

TRAIN_PATH = "ai/datasets/round2_train.jsonl"
VAL_PATH = "ai/datasets/round2_validation.jsonl"

OUTPUT_DIR = "./ai/adapters/lora_round2_gpu"

MAX_LENGTH = 512


# ============================================================
# GPU CHECK
# ============================================================

if not torch.cuda.is_available():
    raise RuntimeError("CUDA GPU is not available.")

device = torch.device("cuda")

print("=" * 60)
print("GPU")
print("=" * 60)
print(torch.cuda.get_device_name(0))
print("CUDA:", torch.version.cuda)
print("BF16:", torch.cuda.is_bf16_supported())


# ============================================================
# TOKENIZER
# ============================================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


# ============================================================
# BASE MODEL
# ============================================================

print("\nLoading Qwen3-0.6B...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16,
)

model = model.to(device)


# ============================================================
# LoRA
# ============================================================

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

    task_type=TaskType.CAUSAL_LM,
)


model = get_peft_model(
    model,
    lora_config
)

model.print_trainable_parameters()


# ============================================================
# DATASET
# ============================================================

print("\nLoading Round-2 dataset...")

dataset = load_dataset(
    "json",
    data_files={
        "train": TRAIN_PATH,
        "validation": VAL_PATH,
    },
)


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize_example(example):

    messages = example["messages"]

    # Build the complete conversation.
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )

    # Build only the user part.
    prompt = tokenizer.apply_chat_template(
        [messages[0]],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    full_tokens = tokenizer(
        text,
        truncation=True,
        max_length=MAX_LENGTH,
        add_special_tokens=False,
    )

    prompt_tokens = tokenizer(
        prompt,
        truncation=True,
        max_length=MAX_LENGTH,
        add_special_tokens=False,
    )

    input_ids = full_tokens["input_ids"]
    attention_mask = full_tokens["attention_mask"]

    labels = input_ids.copy()

    # --------------------------------------------------------
    # Assistant-only loss
    #
    # Everything before the assistant response is masked.
    # The model learns from the expected JSON only.
    # --------------------------------------------------------

    prompt_length = len(prompt_tokens["input_ids"])

    for i in range(
        min(prompt_length, len(labels))
    ):
        labels[i] = -100

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


tokenized_dataset = dataset.map(
    tokenize_example,
    remove_columns=dataset["train"].column_names,
)


# ============================================================
# TRAINING ARGUMENTS
# ============================================================

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    num_train_epochs=1,

    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,

    learning_rate=2e-4,

    logging_steps=50,

    eval_strategy="epoch",
    save_strategy="epoch",

    bf16=True,
    fp16=False,

    use_cpu=False,

    report_to="none",

    seed=42,

    dataloader_num_workers=0,

    save_total_limit=1,

    gradient_checkpointing=False,
)


# ============================================================
# TRAINER
# ============================================================

trainer = Trainer(
    model=model,
    args=training_args,

    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],

    data_collator=DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
    ),
)


# ============================================================
# TRAIN
# ============================================================

print("\n" + "=" * 60)
print("STARTING ROUND-2 TRAINING")
print("=" * 60)

trainer.train()


# ============================================================
# SAVE
# ============================================================

print("\nSaving Round-2 adapter...")

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n" + "=" * 60)
print("ROUND-2 TRAINING COMPLETE")
print("=" * 60)

print("Adapter:", OUTPUT_DIR)
