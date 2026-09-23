#!/bin/bash

COMMAND=$1

function start_cluster() {
    echo "Starting k3d cluster 'followupfinder'..."
    k3d cluster start followupfinder
    
    echo "Starting AI Backend (FastAPI / Swagger)..."
    pkill -f "uvicorn ai.service:app" || true
    
    # Use nohup to detach the process so it survives when the script finishes
    nohup bash -c "source ~/followupfinder-venv/bin/activate && cd '/mnt/d/FOLLOW UP FINDER/followupfinder' && uvicorn ai.service:app --host 0.0.0.0 --port 8000" > ai-backend.log 2>&1 &
    disown
    
    echo "Waiting for core services to become ready (this may take a minute)..."
    kubectl wait --namespace kube-system --for=condition=available deployment/headlamp --timeout=120s
    kubectl wait --namespace argocd --for=condition=available deployment/argocd-server --timeout=120s
    kubectl wait --namespace jenkins --for=condition=ready pod/jenkins-0 --timeout=120s
    
    echo "Setting up port forwards in the background..."
    pkill -f "kubectl.*port-forward" || true
    
    nohup kubectl --namespace kube-system port-forward --address 0.0.0.0 svc/headlamp 8083:80 > /dev/null 2>&1 &
    nohup kubectl --namespace argocd port-forward --address 0.0.0.0 svc/argocd-server 8081:443 > /dev/null 2>&1 &
    nohup kubectl --namespace jenkins port-forward --address 0.0.0.0 svc/jenkins 8082:8080 > /dev/null 2>&1 &
    nohup kubectl --namespace mongodb port-forward --address 0.0.0.0 svc/mongodb 27017:27017 > /dev/null 2>&1 &
    nohup kubectl --namespace jenkins port-forward --address 0.0.0.0 svc/registry-ui 8084:80 > /dev/null 2>&1 &
    nohup kubectl --namespace jenkins port-forward --address 0.0.0.0 svc/followupfinder-registry 5000:5000 > /dev/null 2>&1 &
    disown -a
    
    echo "Opening browser tabs..."
    cmd.exe /c start http://localhost:8083
    cmd.exe /c start https://localhost:8081
    cmd.exe /c start http://localhost:8082
    cmd.exe /c start http://localhost:8000/docs
    cmd.exe /c start http://localhost:8084
    
    echo "Cluster, Swagger, and UI are online! All background services are running."
}

function stop_cluster() {
    echo "Stopping port forwards and AI backend..."
    pkill -f "kubectl.*port-forward" || echo "No port-forwards running."
    pkill -f "uvicorn ai.service:app" || echo "No AI backend running."
    
    echo "Stopping k3d cluster 'followupfinder'..."
    k3d cluster stop followupfinder
    
    echo "Everything is offline! Your laptop battery is safe."
}

if [ "$COMMAND" == "start" ]; then
    start_cluster
elif [ "$COMMAND" == "stop" ]; then
    stop_cluster
else
    echo "Usage: ./manage-cluster.sh [start | stop]"
fi
