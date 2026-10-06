Write-Host "Starting Round 4 Training on GPU..."
& "ai\.venv\Scripts\python.exe" "ai\training\train_lora_round4.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Python training failed! Stopping deployment."
    exit 1
}

Write-Host "Training finished. Copying new adapter to Kubernetes volume..."
New-Item -ItemType Directory -Force -Path "models\lora-round4"
Copy-Item -Path "ai\adapters\lora_round4_gpu\*" -Destination "models\lora-round4\" -Recurse -Force

Write-Host "Updating ArgoCD GitOps..."
(Get-Content "deployment\helm\followupfinder-ai\values.yaml") -replace 'lora-round3', 'lora-round4' | Set-Content "deployment\helm\followupfinder-ai\values.yaml"
git config user.name "AI Assistant"
git config user.email "ai@localhost"
git pull origin feature/setup-infrastructure --rebase
git add "deployment\helm\followupfinder-ai\values.yaml"
git commit -m "Auto-deploy Round 4 model [skip ci]"
git push origin feature/setup-infrastructure

Write-Host "Restarting pods to load Round 4..."
kubectl delete pods -n followupfinder -l app=followupfinder-ai

Write-Host "All done! Round 4 is live."
