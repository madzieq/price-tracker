from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.product import (
    AlertCreate,
    AlertOut,
    ProductCreate,
    ProductList,
    ProductOut,
)
from app.services.ml_service import MLService
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductList)
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Return a paginated list of all tracked products.
    Args:
        skip: number of records to skip (default 0)
        limit: maximum number of records to return (default 100)
        db: database session injected automatically by FastAPI
    Example:
        GET /products/?skip=0&limit=10   → first page
        GET /products/?skip=10&limit=10  → second page
    """
    service = ProductService(db)
    items, total = service.get_all(skip=skip, limit=limit)
    return ProductList(items=items, total=total)   # type: ignore


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """ Add a new product to track and immediately queue it for scraping.
    Args:
        data: product name, URL and scrape interval
        db: database session injected automatically by FastAPI
    Returns:
        newly created product with id, shop name and created_at
    """
    service = ProductService(db)
    product = service.create(data)
    from app.workers.tasks import scrape_product
    scrape_product.delay(product.id)
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """ Return a single product with its full price history and alerts.
    Raises:
        404: if product with given id does not exist
    """
    service = ProductService(db)
    product = service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product was not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """ Delete a product and all its price history and alerts.
    Raises:
        404: if product with given id does not exist
    """
    service = ProductService(db)
    if not service.delete(product_id):
        raise HTTPException(status_code=404, detail="Product was not found")


@router.post("/{product_id}/alerts", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(product_id: int, data: AlertCreate, db: Session = Depends(get_db)):
    """ Create a price alert for a product.
    Alert triggers when scraped price drops at or below threshold_price.
    Args:
        product_id: id of the product to monitor
        data: threshold price and email address to notify
        db: database session injected automatically by FastAPI
    Raises:
        404: if product with given id does not exist
    """
    service = ProductService(db)
    product = service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product was not found")
    return service.add_alert(product_id, data)


@router.get("/{product_id}/forecast")
def get_forecast(product_id: int, days: int = 7, db: Session = Depends(get_db)):
    """ Return ML price forecast and statistics for a product.

    Uses linear regression on price history to predict future price.
    Requires at least 5 price history records to generate a forecast.
    Args:
        product_id: id of the product
        days: how many days ahead to forecast (default 7)
        db: database session injected automatically by FastAPI
    Returns:
        dict with forecast (predicted price, trend, confidence) and statistics (min, max, mean)
    Raises:
        404: if product with given id does not exist
    """
    service = ProductService(db)
    product = service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product was not found")

    ml = MLService()
    history = [
        {"price": p.price, "scraped_at": p.scraped_at}
        for p in product.price_history
    ]
    prices = [p.price for p in product.price_history]

    return {
        "product_id": product_id,
        "forecast": ml.predict_price(history, days_ahead=days),
        "statistics": ml.get_statistics(prices),
    }
