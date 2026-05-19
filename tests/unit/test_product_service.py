import pytest
from unittest.mock import MagicMock, patch
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, AlertCreate


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    return ProductService(mock_db)


def test_extract_shop_allegro(service):
    assert service._extract_shop("https://allegro.pl/oferta/123") == "allegro"


def test_extract_shop_mediamarkt(service):
    assert service._extract_shop("https://www.mediamarkt.pl/product") == "mediamarkt"


def test_extract_shop_unknown(service):
    assert service._extract_shop("https://random-shop.com/item") == "random-shop"


def test_create_product(service, mock_db):
    data = ProductCreate(
        name="Test Laptop",
        url="https://allegro.pl/oferta/test-123",
        scrape_interval_minutes=30,
    )
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    service.create(data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_delete_product_not_found(service, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = service.delete(999)
    assert result is False


def test_check_alerts_triggers_when_price_below_threshold(service, mock_db):
    from datetime import datetime
    from app.models.product import Alert

    alert = Alert(
        id=1,
        product_id=1,
        threshold_price=1000.0,
        email="test@example.com",
        is_active=True,
        triggered_at=None,
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [alert]

    service._check_alerts(product_id=1, current_price=950.0)

    assert alert.triggered_at is not None
    mock_db.commit.assert_called_once()


def test_check_alerts_does_not_trigger_when_price_above(service, mock_db):
    from app.models.product import Alert

    alert = Alert(
        id=1, product_id=1, threshold_price=1000.0,
        email="test@example.com", is_active=True, triggered_at=None,
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [alert]

    service._check_alerts(product_id=1, current_price=1100.0)

    assert alert.triggered_at is None
