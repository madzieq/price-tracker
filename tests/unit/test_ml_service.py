import pytest
from datetime import datetime, timedelta
from app.services.ml_service import MLService


@pytest.fixture
def ml():
    return MLService()


def _make_history(prices: list[float]) -> list[dict]:
    base = datetime(2024, 1, 1)
    return [
        {"price": p, "scraped_at": base + timedelta(days=i)}
        for i, p in enumerate(prices)
    ]


def test_predict_returns_none_when_too_little_data(ml):
    result = ml.predict_price(_make_history([100, 90, 80]))
    assert result["prediction"] is None


def test_predict_returns_forecast_for_sufficient_data(ml):
    prices = [1000, 980, 960, 940, 920, 900, 880]
    result = ml.predict_price(_make_history(prices))
    assert result["predicted_price"] is not None
    assert result["trend"] == "down"
    assert 0 <= result["confidence"] <= 100


def test_predict_trend_up(ml):
    prices = [900, 920, 940, 960, 980, 1000, 1020]
    result = ml.predict_price(_make_history(prices))
    assert result["trend"] == "up"


def test_statistics_basic(ml):
    stats = ml.get_statistics([100.0, 200.0, 300.0])
    assert stats["min"] == 100.0
    assert stats["max"] == 300.0
    assert stats["mean"] == 200.0
    assert stats["current"] == 300.0


def test_statistics_empty(ml):
    assert ml.get_statistics([]) == {}
