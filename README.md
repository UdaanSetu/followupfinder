# FollowupFinder

Repository: `UdaanSetu/followupfinder`

This repository currently contains the FollowupFinder AI experiments and their
datasets, evaluation results, Qwen base model files, and LoRA adapters. The
backend, frontend, database, and deployment areas are reserved for future
implementation.

## Layout

- `ai/inference/` - inference and evaluation code, plus the local Qwen model
- `ai/training/` - LoRA training entry points
- `ai/datasets/` - training, validation, test, and evaluation-result JSONL files
- `ai/adapters/` - preserved LoRA adapters and checkpoints
- `ai/scripts/` - dataset-generation, audit, and analysis utilities
- `docs/` - project documentation and organization records

Large model and optimizer artifacts remain on disk but are excluded by
`.gitignore`. No training or model conversion is performed by this layout
change.
