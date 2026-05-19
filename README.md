# 🛒 Price Tracker

Aplikacja do śledzenia cen produktów online z predykcją trendów ML.

![CI/CD](https://github.com/TWOJ_USERNAME/price-tracker/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/TWOJ_USERNAME/price-tracker/branch/main/graph/badge.svg)

## Stack technologiczny

| Warstwa | Technologie |
|---|---|
| Backend API | FastAPI, SQLAlchemy, Alembic |
| Baza danych | PostgreSQL |
| Cache / kolejka | Redis + Celery |
| Scraping | Selenium (Chrome) |
| ML / analiza | Scikit-learn, Pandas, NumPy |
| Frontend | React + Vite + Recharts |
| Testy | pytest, Robot Framework + SeleniumLibrary |
| CI/CD | GitHub Actions |
| Infrastruktura | Docker, Docker Compose |

## Szybki start

```bash
git clone https://github.com/TWOJ_USERNAME/price-tracker
cd price-tracker

# Uruchom cały stack
docker compose up -d

# API dostępne na:  http://localhost:8000/docs
# Frontend:         http://localhost:3000
# Selenium VNC:     http://localhost:7900
```

## Migracje bazy danych

```bash
cd backend
alembic upgrade head

# Nowa migracja po zmianie modeli:
alembic revision --autogenerate -m "opis zmiany"
```

## Testy

```bash
# Unit testy (szybkie, bez zewnętrznych serwisów)
cd backend
pytest tests/unit -v

# Testy integracyjne (wymaga uruchomionego docker compose)
pytest tests/integration -v

# E2E testy Robot Framework (wymaga pełnego stacku)
robot --outputdir results tests/e2e/tests/
```

## Struktura projektu

```
price-tracker/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # FastAPI endpointy
│   │   ├── core/            # konfiguracja
│   │   ├── db/              # SQLAlchemy setup
│   │   ├── models/          # modele SQL
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # logika biznesowa + ML
│   │   └── workers/         # Celery + Selenium scraper
│   └── alembic/             # migracje DB
├── frontend/
│   └── src/
│       ├── components/      # React komponenty
│       ├── pages/           # widoki
│       └── api/             # klient HTTP
├── tests/
│   ├── unit/                # pytest unit
│   ├── integration/         # pytest integration
│   └── e2e/                 # Robot Framework
│       ├── resources/       # keywords, variables
│       └── tests/           # pliki .robot
└── .github/workflows/       # GitHub Actions
```

## Architektura

```
[React Frontend] → [FastAPI] → [PostgreSQL]
                       ↓
                   [Redis] ← [Celery Beat scheduler]
                       ↓
               [Celery Worker]
                       ↓
            [Selenium Scraper] → ceny → [ML Service]
```

## API Endpoints

| Method | Endpoint | Opis |
|---|---|---|
| GET | `/api/v1/products/` | Lista produktów |
| POST | `/api/v1/products/` | Dodaj produkt |
| GET | `/api/v1/products/{id}` | Szczegóły produktu |
| DELETE | `/api/v1/products/{id}` | Usuń produkt |
| POST | `/api/v1/products/{id}/alerts` | Ustaw alert cenowy |
| GET | `/api/v1/products/{id}/forecast` | Predykcja ML |
| GET | `/health` | Health check |

Pełna dokumentacja: http://localhost:8000/docs
