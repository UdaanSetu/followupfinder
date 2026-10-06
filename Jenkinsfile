pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: docker
                image: docker:24-dind
                args: ["--mtu=1350"]
                securityContext:
                  privileged: true
              - name: jnlp
                image: jenkins/inbound-agent:alpine
                env:
                - name: DOCKER_HOST
                  value: tcp://localhost:2375
            '''
        }
    }
    
    environment {
        // Dynamically use the current branch being built
        GITOPS_BRANCH = "${env.GIT_BRANCH ?: env.BRANCH_NAME ?: 'feature/setup-infrastructure'}"
        DOCKER_REPO = "aditya1961/followupfinder-ai"
    }

    stages {

        stage('AI Tests') {
            steps {
                container('docker') {
                    sh '''
                        apk add --no-cache git
                        cp -r ai ai_test_build
                        rm -f ai_test_build/.dockerignore
                        cat << 'INNER_EOF' > ai_test_build/Dockerfile.test
FROM python:3.11-slim
WORKDIR /app
COPY . /app/ai
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r /app/ai/requirements.txt -r /app/ai/service-requirements.txt pytest
CMD ["python", "-m", "pytest", "ai/tests/"]
INNER_EOF
                        docker build -f ai_test_build/Dockerfile.test -t followupfinder-ai-test:${BUILD_NUMBER} ai_test_build
                        docker run --rm followupfinder-ai-test:${BUILD_NUMBER}
                    '''
                }
            }
            post {
                always {
                    container('docker') {
                        sh 'rm -rf ai_test_build || true'
                    }
                }
            }
        }

        stage('Docker Build') {
            steps {
                container('docker') {
                    sh '''
                        docker build \
                          -f ai/Dockerfile \
                          -t ${DOCKER_REPO}:${BUILD_NUMBER} \
                          ai
                    '''
                }
            }
        }

        stage('Docker Hub Push') {
            steps {
                container('docker') {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-followupfinder', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh '''
                            set +x
                            echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                            set -x
                            
                            docker push ${DOCKER_REPO}:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }

        stage('GitOps Commit') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-followupfinder', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    sh '''
                        # Configure Git specifically for this automated commit
                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"

                        # Safely update ONLY the image tag in values.yaml
                        sed -i "s/^  tag: .*/  tag: \\"${BUILD_NUMBER}\\"/" deployment/helm/followupfinder-ai/values.yaml

                        # Only commit and push if there are actual changes
                        if git diff --exit-code deployment/helm/followupfinder-ai/values.yaml > /dev/null; then
                            echo "values.yaml already has the correct tag. No commit necessary."
                        else
                            git add deployment/helm/followupfinder-ai/values.yaml
                            git commit -m "Update AI image tag to ${BUILD_NUMBER} [skip ci]"
                            
                            set +x # Ensure secrets are not echoed in the log
                            TARGET_BRANCH=$(echo "${GITOPS_BRANCH}" | sed 's|^origin/||')
                            git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/UdaanSetu/followupfinder.git HEAD:${TARGET_BRANCH}
                            set -x
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "FollowUpFinder CI completed successfully. Image version: ${BUILD_NUMBER}"
        }

        failure {
            echo 'FollowUpFinder CI failed.'
        }
    }
}
