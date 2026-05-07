from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings class automatically loads values from .env file
# If a variable is not found in .env, the default value is used
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # General
    APP_NAME: str = "Price Tracker"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"  # used for JWT token signing

    # Database & cache
    DATABASE_URL: str = "postgresql://tracker:tracker123@localhost:5432/pricetracker"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scraper behaviour
    SCRAPE_INTERVAL_MINUTES: int = 30
    MAX_SCRAPE_RETRIES: int = 3

    # Selenium Grid URL (service name "selenium" comes from docker-compose.yml)
    SELENIUM_HUB_URL: str = "http://selenium:4444/wd/hub"

    # Returns True if the app is running in production environment
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

# Single global instance (singleton pattern) — imported across the entire application
# Usage: from app.core.config import settings
settings = Settings()
