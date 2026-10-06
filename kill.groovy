import jenkins.model.*
def build = Jenkins.instance.getItemByFullName("followupfinder-ai-build").getBuildByNumber(3)
if (build != null && build.isBuilding()) {
    build.getExecutor().interrupt()
    println "Killed build 3"
} else {
    println "Build 3 not running"
}
