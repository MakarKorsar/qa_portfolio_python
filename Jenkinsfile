pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Ветка для сборки')
    }

    environment {
        // Определяем переменные окружения
        WORKSPACE = "${pwd()}"
        PYTHONDONTWRITEBYTECODE = '1'  // Избегаем создания .pyc файлов
        PYTHONUNBUFFERED = '1'         // Принудительный вывод в консоль
    }

    stages {
        stage('Checkout') {
            steps {
                // Клонируем репозиторий
                git branch: params.BRANCH_NAME,
                    url: 'https://github.com/MakarKorsar/qa_portfolio_python.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                // Устанавливаем Python зависимости
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    # Устанавливаем pytest и allure-pytest
                    pip install pytest allure-pytest
                '''
            }
        }

        stage('Run API Tests') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        mkdir -p test-results/api
                        pytest tests/api/ --alluredir=test-results/api
                    '''
                }
            }
            post {
                always {
                    // Публикуем результаты тестов
                    allure([
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'test-results/api']]
                    ])
                }
            }
        }

        stage('Run UI Tests') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        mkdir -p test-results/ui
                        pytest tests/ui/ --alluredir=test-results/ui
                    '''
                }
            }
            post {
                always {
                    // Публикуем результаты тестов
                    allure([
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'test-results/ui']]
                    ])
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    // Генерируем Allure отчет из всех результатов тестов
                    sh '''
                        source venv/bin/activate
                        mkdir -p test-results/combined
                        cp -r test-results/api/* test-results/combined/ 2>/dev/null || true
                        cp -r test-results/ui/* test-results/combined/ 2>/dev/null || true
                    '''
                }
            }
            post {
                always {
                    // Публикуем комбинированный отчет
                    allure([
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'test-results/combined']]
                    ])
                }
            }
        }
    }

    post {
        always {
            // Архивируем результаты тестов
            archiveArtifacts artifacts: 'test-results/**', fingerprint: true
            // Публикуем отчеты
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'allure-report',
                reportFiles: 'index.html',
                reportName: 'Allure Report'
            ])
        }
        success {
            echo 'Тесты успешно пройдены!'
        }
        failure {
            echo 'Тесты завершились с ошибками!'
        }
    }
}