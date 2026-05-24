import logging

from app.db.base import SessionLocal
from app.models.product import Product
from app.services.product_service import ProductService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def scrape_product(self, product_id: int):
    from app.workers.scraper import PriceScraper

    db = SessionLocal()
    try:
        service = ProductService(db)
        product = service.get_by_id(product_id)
        if not product or not product.is_active:
            return

        scraper = PriceScraper()
        price = scraper.get_price(product.url)

        if price:
            service.add_price(product_id, price)
            logger.info(f"Scraped {product.name}: {price} PLN")
        else:
            logger.warning(f"Could not scrape price for {product.name}")
    except Exception as exc:
        logger.error(f"Error scraping product {product_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task
def scrape_all_products():
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active).all()
        for product in products:
            scrape_product.delay(product.id)
        logger.info(f"Queued {len(products)} products for scraping")
    finally:
        db.close()
