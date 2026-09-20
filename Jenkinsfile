pipeline {
    agent any

    stages {

        stage('AI Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE/ai:/app" \
                      python:3.11-slim \
                      sh -c "cd /app && pip install --no-cache-dir -r /app/requirements.txt -r /app/service-requirements.txt pytest && python -m pytest /app/tests/"
                '''
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
                '''
            }
        }

        stage('Docker Push') {
            steps {
                sh '''
                    docker push \
                      localhost:5000/followupfinder-ai:${BUILD_NUMBER}
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