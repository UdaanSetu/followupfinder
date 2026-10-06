JENKINS_PW=$(kubectl -n jenkins get secret jenkins -o jsonpath='{.data.jenkins-admin-password}' | base64 -d)
curl -v -u admin:$JENKINS_PW http://localhost:8082/
