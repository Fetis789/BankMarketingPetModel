import joblib

from bank.config import settings

def load_model() -> tuple[object, dict, str]:
    """Если нет model_name (как в CI), то как раньше из joblib. Иначе из реестра MLFlow"""
    if not settings.model_name:
        bundle = joblib.load(settings.model_path)
        return bundle['pipeline'], bundle['metadata'], bundle['metadata']['model_version']
    
    import mlflow
    from mlflow import MlflowClient 
    import mlflow.catboost
    import mlflow.artifacts

    mlflow.set_tracking_uri(settings.mlflow_tracking_url)
    mv = MlflowClient().get_model_version_by_alias(settings.model_name, settings.model_alias)
    pipeline = mlflow.catboost.load_model(f"models:/{settings.model_name}/{mv.version}")
    meta = mlflow.artifacts.load_dict(f"runs:/{mv.run_id}/metadata.json")

    return pipeline, meta, f"{settings.model_name}-v{mv.version}"