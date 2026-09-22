pipeline {
    agent any

    environment {
        DEPLOY_DIR = "/opt/apps/spend-tracker"
        ENV_CREDENTIAL_ID = "spend-tracker-prod-env"

        // Application Port
        APP_PORT = "8080"
    }

    parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run automated pytest suite before deployment')
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out source code from Git...'
                checkout scm
            }
        }

        stage('Automated Tests') {
            when {
                expression { return params.RUN_TESTS }
            }
            steps {
                echo 'Running automated test suite with pytest...'
                sh '''
                    if command -v docker &> /dev/null; then
                        echo "Running tests in isolated Docker container..."
                        docker build -t spend-tracker-test:latest .
                        docker run --rm \
                            -e PYTHONPATH=/app \
                            spend-tracker-test:latest \
                            pytest -v /app/tests                    
                    elif [ -d "venv" ]; then
                        echo "Running tests in existing virtual environment..."
                        . venv/bin/activate
                        pytest -v
                    else
                        echo "Setting up temporary virtual environment for tests..."
                        python3 -m venv .test_venv
                        . .test_venv/bin/activate
                        pip install --no-cache-dir -r requirements.txt
                        pytest -v
                        deactivate
                        rm -rf .test_venv
                    fi
                '''
            }
        }

        stage('Deploy Spend Tracker') {
            steps {
                echo 'Deploying Spend Tracker locally on EC2...'

                withCredentials([
                    file(credentialsId: ENV_CREDENTIAL_ID, variable: 'PROD_ENV_FILE')
                ]) {
                    sh '''
                        echo "Preparing deployment directory..."
                        mkdir -p "${DEPLOY_DIR}"

                        echo "Copying application files..."
                        tar --exclude='.git' \
                            --exclude='.pytest_cache' \
                            --exclude='__pycache__' \
                            --exclude='data' \
                            --exclude='venv' \
                            --exclude='.test_venv' \
                            --exclude='.env' \
                            --exclude='production-env' \
                            -czf - . | tar -xzf - -C "${DEPLOY_DIR}"

                        echo "Installing production environment file..."
                        cp "${PROD_ENV_FILE}" "${DEPLOY_DIR}/.env"
                        chmod 600 "${DEPLOY_DIR}/.env"

                        echo "Building and starting Spend Tracker..."
                        cd "${DEPLOY_DIR}"

                        docker compose -f docker-compose.prod.yml up -d --build

                        echo "Checking Spend Tracker containers..."
                        docker compose -f docker-compose.prod.yml ps
                    '''
                }
            }
        }

        stage('Smoke Test & Health Check') {
            steps {
                echo 'Verifying application health...'

                sh '''
                    echo "Waiting 10 seconds for service warm-up..."
                    sleep 10

                    SUCCESS=0

                    for i in $(seq 1 6); do
                        if curl -sf http://127.0.0.1:${APP_PORT}/health | grep -q '"status":"ok"'; then
                            echo "Health check PASSED on attempt ${i}!"
                            SUCCESS=1
                            break
                        fi

                        echo "Attempt ${i} failed. Retrying in 5 seconds..."
                        sleep 5
                    done

                    if [ ${SUCCESS} -ne 1 ]; then
                        echo "ERROR: Health check failed!"
                        exit 1
                    fi
                '''
            }
        }

    }

    post {
        success {
            echo "=========================================================="
            echo " DEPLOYMENT SUCCESSFUL!"
            echo " Spend Tracker: https://spend-tracker.duckdns.org"
            echo " Swagger Docs:  https://spend-tracker.duckdns.org/docs"
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo " DEPLOYMENT FAILED!"
            echo " Inspect pipeline console logs above for diagnostics."
            echo "=========================================================="
        }
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
