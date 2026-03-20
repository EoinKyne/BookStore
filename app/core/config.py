import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    CART_ITEM_TTL_MINUTES: int = 15

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")
    logger.info(model_config)
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings(_env_file=os.getenv("ENV_FILE", ".env"))
logger.info(f"loaded settings with db host: {settings.POSTGRES_HOST}")
