import jenkins.model.*
def build = Jenkins.instance.getItemByFullName("followupfinder-ai-build").getBuildByNumber(6)
if (build != null && build.isBuilding()) { build.getExecutor().interrupt(); println "Killed build 6" }
