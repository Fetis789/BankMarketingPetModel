from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "artefacts/bank_marketing_model_catboost_bundle.joblib"
    database_url: str | None = None
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}

settings = Settings()