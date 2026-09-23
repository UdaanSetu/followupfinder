#!/bin/bash
IP=$(kubectl get svc followupfinder-registry -n jenkins -o jsonpath='{.spec.clusterIP}')
docker exec k3d-followupfinder-server-0 sh -c "echo '$IP followupfinder-registry.jenkins.svc.cluster.local' >> /etc/hosts"
