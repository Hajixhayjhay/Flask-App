pipeline {
    agent { label 'JenkinsAgent' }

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
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-reports/*.xml', allowEmptyArchive: true
            junit 'test-reports/*.xml'
            cleanWs()
        }
    }
}