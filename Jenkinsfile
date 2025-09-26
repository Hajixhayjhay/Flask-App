pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        GIT_CREDENTIALS = 'github_credentials'
        SONAR_CREDENTIALS = 'sonar_credentials'
        SONAR_PROJECT_KEY = 'FlaskApp'
        SONAR_HOST_URL = 'http://your-sonarqube-server:9000'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: 'dev',
                    url: 'https://github.com/Hajixhayjhay/Flask-App.git',
                    credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source venv/bin/activate
                pytest --junitxml=test-reports/results.xml --cov=flask_app --cov-report xml:coverage.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: SONAR_CREDENTIALS, variable: 'SONAR_TOKEN')]) {
                    sh '''
                    source venv/bin/activate
                    sonar-scanner \
                      -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.login=${SONAR_TOKEN}
                    '''
                }
            }
        }
    }

    post {
        always {
            node {
                archiveArtifacts artifacts: 'test-reports/*, coverage.xml', allowEmptyArchive: true
                cleanWs()
            }
        }
    }
}