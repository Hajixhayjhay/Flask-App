pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV_DIR = 'venv'
        ARTIFACT = 'flaskapp.tar.gz'
        S3_BUCKET = 'aj-flaskapp-bucket'
        SSH_KEY = 'key_file' // your Jenkins SSH credential ID
        SONAR_TOKEN = credentials('SonarQube')      // token
        SONAR_HOST_URL = credentials('Sonar_url')   // Sonar IP/URL
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: 'dev',
                    url: 'https://github.com/Hajixhayjhay/Flask-App.git',
                    credentialsId: 'github_credentials'
            }
        }

        stage('Setup Python') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r flask_app/files/requirements.txt
                    pip install pytest pytest-cov sonar-scanner
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

        stage('SonarQube Analysis') {
            steps {
                sh """
                    source ${VENV_DIR}/bin/activate
                    sonar-scanner \
                        -Dsonar.projectKey=FlaskApp \
                        -Dsonar.sources=flask_app \
                        -Dsonar.host.url=${SONAR_HOST_URL} \
                        -Dsonar.login=${SONAR_TOKEN}
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
                            ansible-playbook -i my_inventory.aws_ec2.yml flaskapp_deploy.yml --extra-vars "artifact_name=${ARTIFACT} s3_bucket=${S3_BUCKET} build_id=latest"
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