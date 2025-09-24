pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/dev']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/Hajixhayjhay/Flask-App.git',
                        credentialsId: 'github_credentials'
                    ]]
                ])
            }
        }

        stage('Setup Python') {
            steps {
                sh """
                python3 -m venv ${VENV}
                ${VENV}/bin/pip install --upgrade pip
                ${VENV}/bin/pip install -r flask_app/files/requirements.txt
                ${VENV}/bin/pip install pytest pytest-cov
                mkdir -p test-reports
                """
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh """
                ${VENV}/bin/pytest flask_app/tests \
                    --junitxml=test-reports/results.xml \
                    --cov=flask_app.files \
                    --cov-report xml:coverage.xml \
                    --cov-report term-missing
                """
            }
        }

        stage('Archive Test Results') {
            steps {
                junit 'test-reports/results.xml'
            }
        }

        stage('Archive Coverage') {
            steps {
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "Build succeeded!"
        }
        failure {
            echo "Build failed. Check test reports and coverage."
        }
    }
}