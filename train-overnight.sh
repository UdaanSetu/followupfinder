#!/bin/bash
set -e
echo 'Starting Round 4 Training on GPU...'
ai/.venv/Scripts/python.exe ai/training/train_lora_round4.py
echo 'Training finished.'
mkdir -p models/lora-round4
cp -r ai/adapters/lora_round4_gpu/* models/lora-round4/
sed -i 's/lora-round3/lora-round4/g' deployment/helm/followupfinder-ai/values.yaml
git pull origin feature/setup-infrastructure --rebase || true
git add deployment/helm/followupfinder-ai/values.yaml
git commit -m 'Auto-deploy Round 4 model' || true
git push origin feature/setup-infrastructure || true
kubectl delete pods -n followupfinder -l app.kubernetes.io/name=followupfinder-ai || true
