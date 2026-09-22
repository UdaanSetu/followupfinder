#!/bin/bash
cat << 'EOF' > jenkins-update.groovy
import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.plugins.credentials.impl.*
import hudson.util.Secret

def domain = Domain.global()
def store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

def newCred = new UsernamePasswordCredentialsImpl(
  CredentialsScope.GLOBAL,
  'github-followupfinder',
  'GitHub PAT',
  'PAT',
  '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'
)

def existing = store.getCredentials(domain).find { it.id == newCred.id }
if (existing) {
    store.removeCredentials(domain, existing)
}
store.addCredentials(domain, newCred)
Jenkins.instance.save()
println 'Jenkins credential updated successfully!'
EOF
JENKINS_PW=$(kubectl -n jenkins get secret jenkins -o jsonpath='{.data.jenkins-admin-password}' | base64 -d)
kubectl exec -n jenkins jenkins-0 -c jenkins -- java -jar /var/jenkins_home/war/WEB-INF/jenkins-cli.jar -s http://localhost:8080/ -auth admin:$JENKINS_PW groovy = < jenkins-update.groovy
