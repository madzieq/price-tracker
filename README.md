# 🛒 Price Tracker

An online product price tracking application with ML trend prediction.

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend API | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Cache / Queue | Redis + Celery |
| Scraping | Selenium (Chrome) |
| ML / Analysis | Scikit-learn, Pandas, NumPy |
| Frontend | React + Vite + Recharts |
| Tests | pytest, Robot Framework + SeleniumLibrary |
| CI/CD | GitHub Actions |
| Infrastructure | Docker, Docker Compose |

## Quick Start

```bash
git clone https://github.com/madzieq/price-tracker
cd price-tracker

# Start the full stack
docker compose up -d

# API available at:  http://localhost:8000/docs
# Frontend:          http://localhost:3000
# Selenium VNC:      http://localhost:7900
```

## Database Migrations

```bash
cd backend

# Apply all migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "description of change"
```

## Tests

```bash
# Unit tests (fast, no external services required)
cd backend
pytest tests/unit -v

# Integration tests (requires docker compose running)
pytest tests/integration -v

# E2E tests with Robot Framework (requires full stack)
robot --outputdir results tests/e2e/tests/
```

## Project Structure

```
price-tracker/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # FastAPI endpoints
│   │   ├── core/            # configuration
│   │   ├── db/              # SQLAlchemy setup
│   │   ├── models/          # SQL models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # business logic + ML
│   │   └── workers/         # Celery + Selenium scraper
│   └── alembic/             # DB migrations
├── frontend/
│   └── src/
│       ├── components/      # React components
│       ├── pages/           # views
│       └── api/             # HTTP client
├── tests/
│   ├── unit/                # pytest unit tests
│   ├── integration/         # pytest integration tests
│   └── e2e/                 # Robot Framework
│       ├── resources/       # keywords, variables
│       └── tests/           # .robot files
└── .github/workflows/       # GitHub Actions
```

## Architecture

```
[React Frontend] → [FastAPI] → [PostgreSQL]
                       ↓
                   [Redis] ← [Celery Beat scheduler]
                       ↓
               [Celery Worker]
                       ↓
            [Selenium Scraper] → prices → [ML Service]
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/products/` | List all products |
| POST | `/api/v1/products/` | Add a new product |
| GET | `/api/v1/products/{id}` | Get product details |
| DELETE | `/api/v1/products/{id}` | Delete a product |
| POST | `/api/v1/products/{id}/alerts` | Set a price alert |
| GET | `/api/v1/products/{id}/forecast` | Get ML price forecast |
| GET | `/health` | Health check |

Full API documentation: http://localhost:8000/docs
