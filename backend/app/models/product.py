from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"  # actual table name in PostgreSQL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Text instead of String — no length limit, suitable for long URLs
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    # Extracted automatically from URL e.g. "allegro"
    shop: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    scrape_interval_minutes: Mapped[int] = mapped_column(Integer, default=30)
    # default=datetime.utcnow — note: no parentheses, SQLAlchemy calls it at insert time
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # One-to-many: one Product has many PriceHistory records
    # cascade="all, delete-orphan" — deleting a product deletes all its price history
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    # One-to-many: one Product can have many alerts
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    # Returns the most recent price by sorting price_history by date
    # Returns None if no prices have been scraped yet
    @property
    def current_price(self) -> float | None:
        if not self.price_history:
            return None
        return sorted(self.price_history, key=lambda x: x.scraped_at)[-1].price


class PriceHistory(Base):
    """ Stores price history for a tracked product.
    A new record is created every time the scraper successfully fetches a price.
    Args:
        product_id: id of the product this price belongs to
        price: scraped price value
        currency: currency code, defaults to "PLN"
        scrape_success: False if scraper found the page but could not extract price
    Example:
        entry = PriceHistory(
            product_id=1,
            price=5299.0,
            currency="PLN"
        )
    """
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    # String(3) — exactly 3 characters, enough for currency codes (PLN, EUR, USD)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    # Indexed because we frequently sort and filter by date
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), index=True)
    scrape_success: Mapped[bool] = mapped_column(Boolean, default=True)

    # Many-to-one: many PriceHistory records belong to one Product
    product: Mapped["Product"] = relationship(back_populates="price_history")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    # Alert triggers when current price drops at or below this value
    threshold_price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # None means the alert has not been triggered yet
    # datetime | None — Python 3.10+ union type syntax (same as Optional[datetime])
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Many-to-one: many Alerts belong to one Product
    product: Mapped["Product"] = relationship(back_populates="alerts")
