import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db

# Use a separate test database
TEST_DATABASE_URL = "postgresql://tracker:tracker123@localhost:5432/pricetracker"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """ Create all tables before each test and drop them after. """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """ Provide a test database session. """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """ Provide a test client with overridden database session. """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ----------- Tests -----------

def test_create_product(client):
    """ Test that POST /products/ creates a new product and returns 201."""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Sony WH-1000XM5",
            "url": "https://allegro.pl/oferta/sony-123",
            "scrape_interval_minutes": 30,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sony WH-1000XM5"
    assert data["shop"] == "allegro"
    assert data["id"] is not None


def test_list_products(client):
    """ Test that GET /products/ returns a list of products. """
    client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "url": "https://allegro.pl/oferta/test-456",
            "scrape_interval_minutes": 30,
        },
    )
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_get_product(client):
    """ Test that GET /products/{id} returns a single product. """
    create = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "url": "https://allegro.pl/oferta/test-789",
            "scrape_interval_minutes": 30,
        },
    )
    product_id = create.json()["id"]
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_get_product_not_found(client):
    """ Test that GET /products/999 returns 404 when product does not exist. """
    response = client.get("/api/v1/products/999")
    assert response.status_code == 404


def test_delete_product(client):
    """ Test that DELETE /products/{id} removes the product. """
    create = client.post(
        "/api/v1/products/",
        json={
            "name": "To Delete",
            "url": "https://allegro.pl/oferta/delete-me",
            "scrape_interval_minutes": 30,
        },
    )
    product_id = create.json()["id"]
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    get = client.get(f"/api/v1/products/{product_id}")
    assert get.status_code == 404


def test_create_alert(client):
    """ Test that POST /products/{id}/alerts creates a price alert. """
    create = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "url": "https://allegro.pl/oferta/alert-test",
            "scrape_interval_minutes": 30,
        },
    )
    product_id = create.json()["id"]
    response = client.post(
        f"/api/v1/products/{product_id}/alerts",
        json={"threshold_price": 1000.0, "email": "test@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["threshold_price"] == 1000.0
    assert data["email"] == "test@example.com"