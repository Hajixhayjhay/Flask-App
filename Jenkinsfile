pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV = 'venv'
        DB_PATH = 'flask_app/files/data.db'
        REQUIREMENTS = 'flask_app/files/requirements.txt'
        ARTIFACT = 'flaskapp.tar.gz'
        S3_BUCKET = 'aj-flaskapp-bucket'
        INVENTORY = 'my_inventory.aws_ec2.yml'
        PLAYBOOK = 'flaskapp_deploy.yml'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    source ${VENV}/bin/activate
                    pip install --upgrade pip
                    pip install -r ${REQUIREMENTS}
                    pip install pytest pytest-cov
                '''
            }
        }

        stage('Initialize DB') {
            steps {
                sh '''
                    sqlite3 ${DB_PATH} < flask_app/files/init_db.sql || true
                '''
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                    source ${VENV}/bin/activate
                    mkdir -p test-reports
                    pytest flask_app/tests \
                        --junitxml=test-reports/results.xml \
                        --cov=flask_app \
                        --cov-report xml:coverage.xml \
                        --cov-report term-missing || true
                '''
            }
        }

        stage('Build & Upload Artifact') {
            steps {
                sh '''
                    tar -czf ${ARTIFACT} flask_app/
                    aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}
                '''
            }
        }

        stage('Deploy via Ansible') {
            steps {
                withCredentials([string(credentialsId: 'key_file', variable: 'KEYFILE')]) {
                    sh '''
                        ansible-playbook -i ${INVENTORY} ${PLAYBOOK} \
                            --private-key $KEYFILE \
                            --extra-vars "artifact=${ARTIFACT} s3_bucket=${S3_BUCKET}"
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-reports/*.xml', allowEmptyArchive: true
            junit 'test-reports/*.xml'
            cleanWs()
        }
    }
}