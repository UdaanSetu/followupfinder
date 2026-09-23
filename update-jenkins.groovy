import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.plugins.credentials.impl.*
import hudson.util.Secret

def domain = Domain.global()
def store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

def newCred = new UsernamePasswordCredentialsImpl(
  CredentialsScope.GLOBAL,
  "github-followupfinder",
  "GitHub PAT for FollowupFinder",
  "UdaanSetu",
  "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"
)

// Check if exists and update, or add
def existing = store.getCredentials(domain).find { it.id == newCred.id }
if (existing) {
    store.updateCredentials(domain, existing, newCred)
    println "Successfully updated credential github-followupfinder"
} else {
    store.addCredentials(domain, newCred)
    println "Successfully added credential github-followupfinder"
}
