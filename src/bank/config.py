from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "artefacts/bank_marketing_model_catboost_bundle.joblib"
    model_name: str | None = None
    model_alias: str = 'champion'
    mlflow_tracking_uri: str = 'http://127.0.0.1:5000'
    database_url: str | None = None
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env", 
        "protected_namespaces": (),
        "extra": "ignore"}

settings = Settings()