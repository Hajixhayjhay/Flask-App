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
                checkout([$class: 'GitSCM',
                          branches: [[name: '*/dev']],
                          userRemoteConfigs: [[url: 'https://github.com/Hajixhayjhay/Flask-App.git',
                                               credentialsId: 'github_credentials']]])
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
                    # Ensure the database exists and initialize tables
                    sqlite3 ${DB_PATH} < flask_app/files/init_db.sql
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
                        --cov=flask_app.files \
                        --cov-report xml:coverage.xml \
                        --cov-report term-missing
                '''
            }
        }

        stage('Build Artifact') {
            steps {
                sh '''
                    tar -czf ${ARTIFACT} flask_app/
                '''
            }
        }

        stage('Upload Artifact to S3') {
            steps {
                sh '''
                    aws s3 cp ${ARTIFACT} s3://${S3_BUCKET}/${ARTIFACT}
                '''
            }
        }

       stage('Deploy via Ansible') {
     steps {
        sh '''
            # Activate virtualenv if needed
            source venv/bin/activate

            # Run the Ansible playbook using your dynamic inventory
            ansible-playbook \
                -i my_inventory.aws_ec2.yml \
                flaskapp_deploy.yml \
                --limit tag_Role_FlaskApp \
                --extra-vars "s3_bucket=aj-flaskapp-bucket"
        '''
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