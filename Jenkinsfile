pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        S3_BUCKET    = 'aj-flaskapp-bucket'   // change if different
        ARTIFACT     = 'flaskapp.tar.gz'
        INVENTORY    = 'my_inventory.aws_ec2.yml'
        PLAYBOOK     = 'flaskapp_deploy.yml'
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
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r flask_app/files/requirements.txt
                    pip install pytest pytest-cov
                '''
            }
        }

        stage('Initialize DB') {
            steps {
                sh '''
                    # Make sure the database file exists
                    sqlite3 flask_app/files/data.db < flask_app/files/init_db.sql
                '''
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                    source venv/bin/activate
                    mkdir -p test-reports
                    pytest flask_app/tests \
                        --junitxml=test-reports/results.xml \
                        --cov=flask_app.files \
                        --cov-report xml:coverage.xml \
                        --cov-report term-missing
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

        stage('Deploy with Ansible') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'JenkinsAgent-key', keyFileVariable: 'KEYFILE')]) {
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