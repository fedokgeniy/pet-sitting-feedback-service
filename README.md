# pet-sitting-feedback-service

Feedback microservice for the pet-sitting platform. Stores reviews,
moderation reports and aggregated sitter ratings. Subscribes to
`BookingCompleted` events from Azure Service Bus to pre-create feedback
placeholders.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy + pyodbc (Azure SQL Database)
- Pydantic v2
- Azure Service Bus (consumer)
- Logging via stdlib `logging`

## Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

OpenAPI: <http://localhost:8002/docs>

## Configuration

`.env` (committed for the student project):

```
DB_USERNAME=pasinozavr
DB_PASSWORD=61YcGTqd
DB_SERVER=tcp:cloud2026.database.windows.net
DB_DATABASE=pr2
ODBC_DRIVER=ODBC Driver 17 for SQL Server

SERVICE_BUS_QUEUE_NAME=vladislavstepanenko
SERVICE_BUS_RECEIVE_CONNECTION_STRING=Endpoint=sb://...
SERVICE_BUS_POLL_INTERVAL_SECONDS=10
LOG_LEVEL=INFO
```

## Endpoints
- `GET /health`
- `POST /init-db` — create `feedback` schema and tables
- `POST /seed` — insert stub data
- `GET /feedback`, `GET /feedback/{id}`, `POST /feedback`
- `GET /rating-aggregates`

## Tests

```bash
pip install pytest flake8
flake8 app tests --max-line-length=120
pytest tests -v
```

## CI

`.github/workflows/ci.yml` runs `flake8` (static analysis) and `pytest`
(unit tests) on every push and pull request.

## Docker

```bash
docker build -t feedback-service .
docker run --rm -p 8002:8000 --env-file .env feedback-service
```
