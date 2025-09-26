pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV_DIR = '/opt/flaskapp/venv'       // Matches your Ansible playbook
        ARTIFACT = 'flaskapp.tar.gz'
        S3_BUCKET = 'aj-flaskapp-bucket'
        SSH_KEY = 'key_file'                  // Jenkins SSH credential ID
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python & Install Dependencies') {
            steps {
                sh """
                    set -e
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r flask_app/files/requirements.txt
                    pip install pytest pytest-cov
                """
            }
        }

        stage('Initialize SQLite DB') {
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
                    cd flask_app
                    tar -czf ../${ARTIFACT} *
                    cd ..
                    aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}
                """
            }
        }

        stage('Deploy via Ansible') {
            steps {
                sshagent([SSH_KEY]) {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws_credentials']]) {
                        sh """
                            ansible-playbook -i my_inventory.aws_ec2.yml flaskapp_deploy.yml \
                            --extra-vars "artifact_name=${ARTIFACT} s3_bucket=${S3_BUCKET} build_id=latest venv_dir=${VENV_DIR}"
                        """
                    }
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