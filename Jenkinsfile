pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        BUCKET_NAME = "YOUR_BUCKET_NAME" // replace with your S3 bucket
        ARTIFACT_NAME = "flaskapp.tar.gz"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout([$class: 'GitSCM', 
                          branches: [[name: '*/dev']],
                          userRemoteConfigs: [[url: 'https://github.com/Hajixhayjhay/Flask-App.git', credentialsId: 'github_credentials']]])
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv ${VENV_DIR}
                source ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -r flask_app/files/requirements.txt
                pip install pytest pytest-cov
                '''
            }
        }

        stage('Initialize DB') {
            steps {
                sh '''
                source ${VENV_DIR}/bin/activate
                sqlite3 flask_app/files/data.db < /dev/null
                '''
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                source ${VENV_DIR}/bin/activate
                mkdir -p test-reports
                pytest flask_app/tests --junitxml=test-reports/results.xml --cov=flask_app.files --cov-report xml:coverage.xml --cov-report term-missing
                '''
            }
        }

        stage('Build Artifact') {
            steps {
                sh '''
                tar -czf ${ARTIFACT_NAME} flask_app/
                '''
            }
        }

        stage('Upload Artifact to S3') {
            steps {
                sh '''
                aws s3 cp ${ARTIFACT_NAME} s3://${BUCKET_NAME}/${ARTIFACT_NAME}
                '''
            }
        }

        stage('Deploy via Ansible') {
            steps {
                sh '''
                ansible-playbook -i my_inventory.aws_ec2.yml flaskapp_deploy.yml
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-reports/results.xml', allowEmptyArchive: true
            junit 'test-reports/results.xml'
            cleanWs()
        }
    }
}
