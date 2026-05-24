from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import products
from app.core.config import settings

# Main FastAPI application instance
# title, description and version are visible in Swagger UI at /docs
app = FastAPI(
    title=settings.APP_NAME,
    description="Online product price tracking application with ML price prediction",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (Cross-Origin Resource Sharing) middleware
# Allows the React frontend (localhost:3000) to make requests to this API (localhost:8000)
# Without this, the browser would block all requests from a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the products router — all product endpoints will be available under /api/v1
# e.g. GET /api/v1/products/, POST /api/v1/products/, GET /api/v1/products/{id}
app.include_router(products.router, prefix="/api/v1")

# Simple health check endpoint — used by Docker and CI/CD to verify the app is running
# GET /health → {"status": "ok", "app": "Price Tracker"}
@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
