pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV = "${WORKSPACE}/venv"
        S3_BUCKET = "your-s3-bucket-name"  // Replace with your S3 bucket
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
                    --cov=flask_app \
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

        stage('Create Artifact') {
            steps {
                sh """
                tar -czf flask-app-artifact.tar.gz flask_app/ flask_app/files/ requirements.txt
                """
            }
        }

        stage('Upload Artifact to S3') {
            steps {
                withAWS(credentials: 'aws_credentials', region: 'us-east-1') {
                    s3Upload(bucket: "${S3_BUCKET}", path: "flask-app-artifact.tar.gz", file: "flask-app-artifact.tar.gz")
                }
            }
        }

        stage('Deploy App via Ansible') {
            steps {
                ansiblePlaybook(
                    playbook: 'flaskapp_deploy.yml',
                    inventory: 'inventory/hosts',
                    extras: '--tags deploy'
                )
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "Build, test, and deployment succeeded!"
        }
        failure {
            echo "Build or deployment failed. Check test reports and logs."
        }
    }
}