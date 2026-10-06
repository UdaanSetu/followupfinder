#!/bin/bash
JENKINS_PW=$(kubectl -n jenkins get secret jenkins -o jsonpath='{.data.jenkins-admin-password}' | base64 -d)
kubectl exec -n jenkins jenkins-0 -c jenkins -i -- java -jar /tmp/jenkins-cli.jar -s http://jenkins:8080/ -webSocket -auth admin:$JENKINS_PW groovy = < update-jenkins.groovy
