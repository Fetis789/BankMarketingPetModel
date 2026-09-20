# Bank Marketing Prediction

## Выбранный датасет и модель

В качестве датасета взял датасет [Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing). В данном датасете необходимо предсказать отклик клиента на звонок с маркетинговым посылом - задача классификации с двумя классами - 1 (клиент среагировал) и 0 (клиент не среагировал).
ipynb-ноутбук с обучением модели, подбором гиперпараметров и сужением фичей до определенного числа без потери результата лежит по пути artefacts/Bank Marketing Baseline.ipynb. 

Результаты модели на суженном множестве самых важных фичей (для оптимизации на проде) и на всех фичах на тестовом датасете.

| Метрика | Значение на всех фичах | Значение на 10 выбранных фичах |
|----------|--------|------------|
| ROC_AUC | 0.813 | 0.808 |
| PR_AUC | 0.488 | 0.428 |
| Accuracy | 0.885 | 0.881 |
| Precision | 0.491 | 0.477 |
| Recall | 0.572 | 0.561 |
| F1 | 0.528 | 0.516 |

Можно заметить, что результаты не сильно отличаются для сужения на 10 фичей и для всех 16 фичей. Поэтому для оптимизации процессов на проде быдло принято решение оставить 10 фичей в модели.

## Сам сервис

### Быстрый запуск

Вначале посмотрим полный набор команд (с учетом некоторых изменений в именах), которые неоходимо выполнить, чтобы запустить сервис локально, после docker compose и через kubernetes.

1. Клонирование репозитория, тесты и запуск локально + curl для проверки
```bash
git clone https://github.com/Fetis789/BankMarketingPetModel.git
cd BankMarketingPetModel

uv sync (можно с --locked)
uv run pytest
uv run uvicorn bank.service.app:app ‐‐port 8000
curl.exe -X POST "localhost:8000/v1/predict" -H "Content-Type: application/json" -d "@good_example.json"
```

2. Сбор через docker и docker-compose, проверка базы
```bash
docker build ‐t bank‐service:1.0 .
docker compose up ‐d ‐‐build
curl.exe -X POST "localhost:8000/v1/predict" -H "Content-Type: application/json" -d "@good_example.json"
docker compose exec db psql -U postgres -d bank_marketing -c "SELECT request_id, score, latency_ms, model_version from predictions;" (проверка БД)
```

3. Запуск кластера на kubernetes
```bash
kind create cluster ‐‐name mlpro
kind load docker‐image bank‐service:1.0 ‐‐name mlpro
kubectl apply ‐f k8s/
kubectl rollout status deploy/bank‐service
kubectl port‐forward service/churn‐service 8080:80
curl.exe -X POST "localhost:8080/v1/predict" -H "Content-Type: application/json" -d "@good_example.json"
```

Теперь немного подробнее остановимся на каждом этапе со скринами результатов и основными проблемами
### Локальный запуск

У меня изначально была проблема в том, что я принял неверное решение в ipynb ноуте сразу сделать сласс