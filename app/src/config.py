from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Apex Retail Order Management"
    app_env: str = "onprem-baseline"
    debug: bool = False
    database_url: str = "postgresql://app_user:SourcePass2026!@postgres:5432/orders_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
