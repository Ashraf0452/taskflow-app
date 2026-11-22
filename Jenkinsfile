
pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        GHCR_OWNER = 'ashraf0452'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    set -eu
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install -r requirements.txt
                    python -m unittest discover -s tests -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=12 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_URI = "ghcr.io/${env.GHCR_OWNER}/taskflow:${env.IMAGE_TAG}"
                }

                sh 'docker build -t "$IMAGE_URI" .'
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-pat',
                        usernameVariable: 'GH_USER',
                        passwordVariable: 'GH_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        set +x

                        printf '%s' "$GH_TOKEN" | docker login ghcr.io -u "$GH_USER" --password-stdin

                        docker push "$IMAGE_URI"

                        docker logout ghcr.io
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "CI SUCCESS: ${env.IMAGE_URI}"
        }
        failure {
            echo 'CI FAILED: Check Console Output'
        }
    }
}
