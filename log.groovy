import jenkins.model.*
def job = Jenkins.instance.getItemByFullName("followupfinder-ai-build")
if (job != null) {
    def build = job.getLastBuild()
    if (build != null) {
        def log = build.getLog(50)
        log.each { println it }
    } else {
        println "No builds found."
    }
} else {
    println "Job not found."
}
