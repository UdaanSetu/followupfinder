#!/bin/bash

COMMAND=$1

function start_cluster() {
    echo "🚀 Starting k3d cluster 'followupfinder'..."
    k3d cluster start followupfinder
    
    echo "⏳ Waiting for core services to become ready (this may take a minute)..."
    # Wait for the deployments to be available
    kubectl wait --namespace kube-system --for=condition=available deployment/headlamp --timeout=120s
    kubectl wait --namespace argocd --for=condition=available deployment/argocd-server --timeout=120s
    kubectl wait --namespace jenkins --for=condition=ready pod -l app.kubernetes.io/instance=jenkins --timeout=120s
    
    echo "🔌 Setting up port forwards in the background..."
    # Kill any existing port forwards first to prevent port conflicts
    pkill -f "kubectl.*port-forward" || true
    
    kubectl --namespace kube-system port-forward svc/headlamp 8083:80 > /dev/null 2>&1 &
    kubectl --namespace argocd port-forward svc/argocd-server 8081:443 > /dev/null 2>&1 &
    kubectl --namespace jenkins port-forward svc/jenkins 8082:8080 > /dev/null 2>&1 &
    kubectl --namespace mongodb port-forward svc/mongodb 27017:27017 > /dev/null 2>&1 &
    
    echo "🌐 Opening browser tabs..."
    # cmd.exe allows us to open the default Windows browser from inside Linux!
    cmd.exe /c start http://localhost:8083
    cmd.exe /c start https://localhost:8081
    cmd.exe /c start http://localhost:8082

    echo ""
    echo "=================================================="
    echo "🔑 LOGIN CREDENTIALS"
    echo "=================================================="
    echo "[ArgoCD] (https://localhost:8081)"
    echo "  Username: admin"
    ARGOCD_PW=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)
    echo "  Password: $ARGOCD_PW"
    echo ""
    echo "[Jenkins] (http://localhost:8082)"
    echo "  Username: admin"
    JENKINS_PW=$(kubectl -n jenkins get secret jenkins -o jsonpath='{.data.jenkins-admin-password}' | base64 -d)
    echo "  Password: $JENKINS_PW"
    echo "=================================================="
    echo ""
    
    echo "✅ Cluster and UI are online! All port-forwards are running in the background."
    echo "⚠️  Keep this terminal open to maintain the port-forwards. Press Ctrl+C to stop."
    wait
}

function stop_cluster() {
    echo "🛑 Stopping port forwards..."
    pkill -f "kubectl.*port-forward" || echo "No port-forwards running."
    
    echo "🛑 Stopping k3d cluster 'followupfinder'..."
    k3d cluster stop followupfinder
    
    echo "💤 Cluster offline! Your laptop battery is safe."
}

if [ "$COMMAND" == "start" ]; then
    start_cluster
elif [ "$COMMAND" == "stop" ]; then
    stop_cluster
else
    echo "Usage: ./manage-cluster.sh [start | stop]"
fi

