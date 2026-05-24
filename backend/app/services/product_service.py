import re
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.product import Alert, PriceHistory, Product
from app.schemas.product import AlertCreate, ProductCreate


class ProductService:
    """Service layer for all product-related business logic."""

    def __init__(self, db: Session):
        """Inject the database session — allows easy mocking in tests."""
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[type[Product]], int]:
        """Return a paginated list of products and the total count.
        Args:
            skip: number of records to skip (for pagination)
            limit: maximum number of records to return
        Returns:
            tuple of (list of products, total count)
        """
        total = self.db.query(Product).count()
        items = self.db.query(Product).offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, product_id: int) -> type[Product] | None:
        """Return a single product by id, or None if not found."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, data: ProductCreate) -> Product:
        """Create a new product and save it to the database.
        Automatically extracts the shop name from the URL.
        """
        # HttpUrl is not a plain string — convert it first
        url_str = str(data.url)
        shop = self._extract_shop(url_str)
        product = Product(
            name=data.name,
            url=url_str,
            shop=shop,
            scrape_interval_minutes=data.scrape_interval_minutes,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        """Delete a product by id.
        Returns:
            True if deleted, False if product was not found
        """
        product = self.get_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def add_price(
        self, product_id: int, price: float, currency: str = "PLN"
    ) -> PriceHistory:
        """Save a new price entry and check if any alerts should be triggered."""
        entry = PriceHistory(product_id=product_id, price=price, currency=currency)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        self._check_alerts(product_id, price)
        return entry

    def add_alert(self, product_id: int, data: AlertCreate) -> Alert:
        """Create a price alert for a product."""
        alert = Alert(
            product_id=product_id,
            threshold_price=data.threshold_price,
            email=data.email,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def _check_alerts(self, product_id: int, current_price: float) -> None:
        """Check all active alerts for a product and trigger them if price dropped below threshold."""
        alerts = (
            self.db.query(Alert)
            .filter(Alert.product_id == product_id, Alert.is_active)
            .all()
        )
        for alert in alerts:
            if current_price <= alert.threshold_price:
                alert.triggered_at = datetime.now(UTC)
                self.db.commit()

    @staticmethod
    def _extract_shop(url: str) -> str:
        """Extract shop name from URL.
        Examples:
            "https://www.allegro.pl/offer/123" → "allegro"
            "https://mediamarkt.pl/product"    → "mediamarkt"
        """
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if match:
            domain = match.group(1)
            return domain.split(".")[0]
        return "unknown"
