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
