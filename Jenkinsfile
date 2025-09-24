pipeline {
    agent {
        label 'JenkinsAgent'   // Jenkins agent builds the code
    }

    environment {
        APP_NAME = 'flaskapp'
        BUILD_ID = "${env.BUILD_NUMBER}"
        ARTIFACT = "${APP_NAME}_${BUILD_ID}.tar.gz"
        S3_BUCKET = 'aj-flaskapp-bucket'
        VENV_DIR = 'venv'
        DEPLOY_PLAYBOOK = 'flaskapp_deploy.yml'
        INVENTORY_FILE = 'my_inventory.aws_ec2.yml'
        GIT_CREDENTIALS = 'github_credentials'
        AWS_CREDENTIALS = 'aws_credentials'
        EMAIL_CREDENTIALS = 'email_credentials'
        FLASK_PORT = 'flask_port'  // Optional, for reference
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS}",
                                                 usernameVariable: 'GIT_USER',
                                                 passwordVariable: 'GIT_PASS')]) {
                    git branch: 'main', 
                        url: "https://$GIT_USER:$GIT_PASS@github.com/your-repo/flaskapp.git"
                }
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh './${VENV_DIR}/bin/pip install --upgrade pip'
                sh './${VENV_DIR}/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh './${VENV_DIR}/bin/pytest --junitxml=test-reports/results.xml --cov=. --cov-report xml:coverage.xml'
            }
            post {
                always {
                    junit 'test-reports/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }

        stage('Package Artifact') {
            steps {
                sh "tar -czf ${ARTIFACT} *"
            }
        }

        stage('Upload to S3') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', 
                                  credentialsId: "${AWS_CREDENTIALS}"]]) {
                    sh "aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}"
                }
            }
        }

        stage('Deploy via Ansible') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                // Deploy to your app server group
                ansiblePlaybook(
                    playbook: "${DEPLOY_PLAYBOOK}",
                    inventory: "${INVENTORY_FILE}",
                    extras: "--limit flask-app-servers -e artifact=${ARTIFACT}"
                )
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${ARTIFACT}", allowEmptyArchive: false
        }
        success {
            echo "Build and deployment succeeded for build #${BUILD_NUMBER}"
        }
        failure {
            withCredentials([usernamePassword(credentialsId: "${EMAIL_CREDENTIALS}", 
                                             usernameVariable: 'EMAIL_USER', 
                                             passwordVariable: 'EMAIL_PASS')]) {
                mail to: 'you@example.com',
                     subject: "Build Failed: ${currentBuild.fullDisplayName}",
                     body: "Check Jenkins for details: ${env.BUILD_URL}"
            }
        }
    }
}
