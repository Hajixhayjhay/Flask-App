pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV_DIR = 'venv'
        ARTIFACT = 'flaskapp.tar.gz'
        S3_BUCKET = 'aj-flaskapp-bucket'
        SSH_KEY = 'key_file' // your Jenkins SSH credential ID
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r flask_app/files/requirements.txt
                    pip install pytest pytest-cov
                """
            }
        }

        stage('Initialize DB') {
            steps {
                sh """
                    sqlite3 flask_app/files/data.db < flask_app/files/init_db.sql
                """
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh """
                    source ${VENV_DIR}/bin/activate
                    mkdir -p test-reports
                    pytest flask_app/tests \
                        --junitxml=test-reports/results.xml \
                        --cov=flask_app \
                        --cov-report xml:coverage.xml \
                        --cov-report term-missing
                """
            }
        }

        stage('Build & Upload Artifact') {
            steps {
                sh """
                    tar -czf ${ARTIFACT} flask_app/
                    aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}
                """
            }
        }

        stage('Deploy via Ansible') {
            steps {
                sshagent([SSH_KEY]) {
                    sh """
                        ansible-playbook -i flaskapp_deploy.yml flaskrole/main.yml \
                            --extra-vars "artifact=${ARTIFACT} s3_bucket=${S3_BUCKET}"
                    """
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-reports/*, coverage.xml', allowEmptyArchive: true
            junit 'test-reports/results.xml'
            cleanWs()
        }
    }
}