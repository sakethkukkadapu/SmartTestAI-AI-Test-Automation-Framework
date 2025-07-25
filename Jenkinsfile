pipeline {
    agent {
        docker {
            image 'python:3.9'
            args '-v ${WORKSPACE}:/app'
        }
    }
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
        OPENAI_API_KEY = credentials('openai-api-key')
        SLACK_WEBHOOK_URL = credentials('slack-webhook-url')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'cp .env.example .env'
                sh 'echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env'
                sh 'echo "SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}" >> .env'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'pip install flake8'
                sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
            }
        }
        
        stage('Test') {
            steps {
                sh 'python runner.py --all --parallel --report-formats html junit'
            }
            post {
                always {
                    junit 'reports/*.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: '*.html',
                        reportName: 'Test Report'
                    ])
                }
            }
        }
        
        stage('Notify') {
            steps {
                sh 'python runner.py --notify --detailed-notify'
            }
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
        }
    }
    
    post {
        success {
            echo 'All tests passed!'
        }
        failure {
            echo 'Tests failed!'
        }
        always {
            archiveArtifacts artifacts: 'reports/*, logs/*', allowEmptyArchive: true
        }
    }
}
