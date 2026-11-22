
pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
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

        stage('Update GitOps Repository') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'gitops-pat',
                        usernameVariable: 'GITOPS_USER',
                        passwordVariable: 'GITOPS_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        set +x

                        # Authenticate Git without putting the token in the URL
                        ASKPASS_FILE="$(mktemp)"
                        trap 'rm -f "$ASKPASS_FILE"' EXIT

                        echo '#!/bin/sh' > "$ASKPASS_FILE"
                        echo 'case "$1" in' >> "$ASKPASS_FILE"
                        echo '  *Username*) echo "$GITOPS_USER" ;;' >> "$ASKPASS_FILE"
                        echo '  *Password*) echo "$GITOPS_TOKEN" ;;' >> "$ASKPASS_FILE"
                        echo 'esac' >> "$ASKPASS_FILE"

                        chmod 700 "$ASKPASS_FILE"
                        export GIT_ASKPASS="$ASKPASS_FILE"
                        export GIT_TERMINAL_PROMPT=0

                        # Clone the GitOps repository
                        rm -rf gitops

                        git clone --branch main --single-branch \
                          https://github.com/Ashraf0452/taskflow-gitops.git gitops

                        cd gitops

                        # Update the Docker image tag
                        sed -i \
                          "s#image: ghcr.io/ashraf0452/taskflow:.*#image: ${IMAGE_URI}#" \
                          kubernetes/deployment.yaml

                        grep -F "image: ${IMAGE_URI}" kubernetes/deployment.yaml

                        # Commit and push only when something changed
                        if git diff --quiet -- kubernetes/deployment.yaml; then
                            echo "GitOps already uses this image"
                        else
                            git config user.name "TaskFlow Jenkins"
                            git config user.email "taskflow-jenkins@users.noreply.github.com"

                            git add kubernetes/deployment.yaml

                            git commit -m "ci: deploy TaskFlow ${IMAGE_TAG}"

                            git push origin HEAD:main
                        fi
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

