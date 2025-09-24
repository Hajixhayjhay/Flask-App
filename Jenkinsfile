pipeline {
    agent { label 'JenkinsAgent' }

    environment {
        APP_NAME = 'flaskapp'
        BUILD_ID = "${env.BUILD_NUMBER}"
        ARTIFACT = "${APP_NAME}_${BUILD_ID}.tar.gz"
        S3_BUCKET = 'aj-flaskapp-bucket'
        VENV_DIR = 'venv'
        DEPLOY_PLAYBOOK = 'flaskapp_deploy.yml'
        INVENTORY_FILE = 'my_inventory.aws_ec2.yml'
        GIT_CREDENTIALS = 'git_credentials'
        AWS_CREDENTIALS = 'aws_credentials'
        EMAIL_CREDENTIALS = 'email_credentials'
        SONAR_TOKEN = 'sonar_token'
        SONARQUBE_ENV = 'SonarQube'
        FLASK_PORT = '5000'
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: 'dev',
                    url: 'https://github.com/Hajixhayjhay/Flask-App.git',
                    credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh './${VENV_DIR}/bin/pip install --upgrade pip'
                sh './${VENV_DIR}/bin/pip install -r flask_app/files/requirements.txt'
                sh './${VENV_DIR}/bin/pip install pytest pytest-cov'
            }
        }

        stage('Run Tests') {
            steps {
                sh './${VENV_DIR}/bin/pytest flask_app/tests --junitxml=test-reports/results.xml --cov=flask_app/files --cov-report xml:coverage.xml'
            }
            post {
                always {
                    junit 'test-reports/*.xml'
                    // Remove Cobertura for now (plugin missing)
                    // cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    withCredentials([string(credentialsId: "${SONAR_TOKEN}", variable: 'SONAR_TOKEN')]) {
                        sh "./${VENV_DIR}/bin/pip install sonar-scanner"
                        sh "sonar-scanner -Dsonar.projectKey=${APP_NAME} -Dsonar.sources=flask_app/files -Dsonar.python.coverage.reportPaths=coverage.xml -Dsonar.login=$SONAR_TOKEN"
                    }
                }
            }
        }

        stage('Package Artifact') {
            steps {
                sh "tar -czf ${ARTIFACT} flask_app/files/*"
            }
        }

        stage('Upload to S3') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS}"]]) {
                    sh "aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}"
                }
            }
        }

        stage('Deploy via Ansible') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
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
            withCredentials([usernamePassword(credentialsId: "${EMAIL_CREDENTIALS}", usernameVariable: 'EMAIL_USER', passwordVariable: 'EMAIL_PASS')]) {
                mail to: 'you@example.com',
                     subject: "Build Failed: ${currentBuild.fullDisplayName}",
                     body: "Check Jenkins for details: ${env.BUILD_URL}"
            }
        }
    }
}