from pydantic_settings import  BaseSettings

class Settings(BaseSettings):
    model_path: str = "artefacts/bank_marketing_catboost_bundle.joblib"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bank_marketing"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}

settings = Settings()