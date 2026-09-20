pipeline {
    agent any

    stages {

        stage('AI Tests') {
            steps {
                sh '''
                    cp -r ai ai_test_build
                    rm -f ai_test_build/.dockerignore
                    cat << 'EOF' > ai_test_build/Dockerfile.test
FROM python:3.11-slim
WORKDIR /app
COPY . /app/ai
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r /app/ai/requirements.txt -r /app/ai/service-requirements.txt pytest
CMD ["python", "-m", "pytest", "ai/tests/"]
EOF
                    docker build -f ai_test_build/Dockerfile.test -t followupfinder-ai-test:${BUILD_NUMBER} ai_test_build
                    docker run --rm followupfinder-ai-test:${BUILD_NUMBER}
                '''
            }
            post {
                always {
                    sh 'rm -rf ai_test_build || true'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                      -f ai/Dockerfile \
                      -t followupfinder-ai:${BUILD_NUMBER} \
                      ai
                '''
            }
        }

        stage('Docker Tag') {
            steps {
                sh '''
                    docker tag \
                      followupfinder-ai:${BUILD_NUMBER} \
                      localhost:5000/followupfinder-ai:${BUILD_NUMBER}
                      
                    docker tag \
                      followupfinder-ai:${BUILD_NUMBER} \
                      localhost:5000/followupfinder-ai:latest
                '''
            }
        }

        stage('Docker Push') {
            steps {
                sh '''
                    docker push \
                      localhost:5000/followupfinder-ai:${BUILD_NUMBER}
                      
                    docker push \
                      localhost:5000/followupfinder-ai:latest
                '''
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