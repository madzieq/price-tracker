from datetime import datetime
from pydantic import BaseModel, HttpUrl, EmailStr

# "Out" suffix — this schema is used for API RESPONSES (sending data to the client)
# "Create" suffix — this schema is used for API REQUESTS (receiving data from the client)

# Represents a single price history entry returned by the API (GET response)
class PriceHistoryOut(BaseModel):
    id: int
    price: float
    currency: str
    scraped_at: datetime

    model_config = {"from_attributes": True}


# Data required to CREATE a new alert — received from the client (POST request)
# POST /products/{id}/alerts
class AlertCreate(BaseModel):
    threshold_price: float
    email: EmailStr


# Represents an alert returned by the API (GET response)
class AlertOut(BaseModel):
    id: int
    threshold_price: float
    is_active: bool
    triggered_at: datetime | None
    email: str

    model_config = {"from_attributes": True}


# Data required to CREATE a new product — received from the client (POST request)
# POST /products/
class ProductCreate(BaseModel):
    name: str
    url: HttpUrl
    scrape_interval_minutes: int = 30


# Represents a full product returned by the API, including related data (GET)
# GET /products/{id}
class ProductOut(BaseModel):
    id: int
    name: str
    url: str
    shop: str | None
    is_active: bool
    current_price: float | None
    created_at: datetime
    price_history: list[PriceHistoryOut] = []
    alerts: list[AlertOut] = []

    model_config = {"from_attributes": True}


# Used for paginated list responses — wraps a list of products with a total count
class ProductList(BaseModel):
    items: list[ProductOut]
    total: int  # total number of products in the database (not just on this page)
