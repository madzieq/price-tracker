import pytest
from unittest.mock import MagicMock
from pydantic import HttpUrl
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, AlertCreate
from app.models.product import Product, Alert, PriceHistory


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


@pytest.fixture
def service(mock_db):
    return ProductService(mock_db)


@pytest.fixture
def sample_alert():
    return Alert(
        id=1,
        product_id=1,
        threshold_price=1000.0,
        email="test@example.com",
        is_active=True,
        triggered_at=None,
    )


@pytest.fixture
def sample_alert_create():
    return AlertCreate(threshold_price=800.0, email="test@example.com")


def test_extract_shop_allegro(service):
    """ Test that extract_shop() returns allegro shop from url. """
    assert service._extract_shop("https://allegro.pl/oferta/123") == "allegro"


def test_extract_shop_mediamarkt(service):
    """ Test that extract_shop() returns mediamarkt shop from url. """
    assert service._extract_shop("https://www.mediamarkt.pl/product") == "mediamarkt"


def test_extract_shop_unknown(service):
    """ Test that extract_shop() returns expected shop from url. """
    assert service._extract_shop("https://random-shop.com/item") == "random-shop"


def test_create_product(service, mock_db):
    """ Test that create method saves a new Product entry to the database. """
    data = ProductCreate(
        name="Test Laptop",
        url=HttpUrl("https://allegro.pl/oferta/test-123"),
        scrape_interval_minutes=30,
    )

    result = service.create(data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    assert isinstance(result, Product)


def test_delete_product_not_found(service, mock_db):
    """ Test that delete() returns False when product does not exist. """
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = service.delete(999)
    assert result is False


def test_add_price_saves_entry(service, mock_db):
    """ Test that add_price saves a new PriceHistory entry to the database. """
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = service.add_price(product_id=1, price=999.0)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called()
    assert isinstance(result, PriceHistory)


def test_add_price_default_currency_is_pln(service, mock_db):
    """ Test that default currency is PLN when not specified. """
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = service.add_price(product_id=1, price=999.0)

    assert result.currency == "PLN"


def test_add_alert_saves_alert(service, mock_db, sample_alert_create):
    """ Test that add_alert saves a new Alert to the database. """
    result = service.add_alert(product_id=1, data=sample_alert_create)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    assert isinstance(result, Alert)


def test_add_alert_sets_correct_threshold(service, mock_db, sample_alert_create):
    """ Test that alert is created with the correct threshold price. """
    result = service.add_alert(product_id=1, data=sample_alert_create)

    assert result.threshold_price == 800.0
    assert result.email == "test@example.com"


def test_check_alerts_triggers_when_price_below_threshold(service, mock_db, sample_alert):
    """ Test that alert is triggered when current price drops below threshold. """
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_alert]

    service._check_alerts(product_id=1, current_price=950.0)

    assert sample_alert.triggered_at is not None
    mock_db.commit.assert_called_once()


def test_check_alerts_does_not_trigger_when_price_above(service, mock_db, sample_alert):
    """ Test that alert is not triggered when current price is above threshold. """
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_alert]

    service._check_alerts(product_id=1, current_price=1100.0)

    assert sample_alert.triggered_at is None
