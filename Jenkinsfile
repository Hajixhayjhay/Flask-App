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
                # Create venv only if it doesn't exist
                [ ! -d "${VENV}" ] && python3 -m venv ${VENV}

                # Activate venv and install requirements
                source ${VENV}/bin/activate
                pip install --upgrade pip
                pip install -r flask_app/files/requirements.txt
                pip install pytest pytest-cov

                mkdir -p test-reports
                """
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh """
                source ${VENV}/bin/activate
                pytest flask_app/tests \
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