#!/bin/bash
kubectl patch application followupfinder-ai -n argocd --type merge -p '{"operation":{"sync":{"revision":"feature/setup-infrastructure"}}}'
