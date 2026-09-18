import psycopg
from psycopg.types.json import Json

from bank.config import settings

DDL = """
CREATE TABLE IF NOT EXISTS predictions (

    request_id      uuid PRIMARY KEY,
    ts      timestamptz NOT NULL DEFAULT now(),
    model_version       text NOT NULL,
    features        jsonb NOT NULL,
    score       double precision NOT NULL,
    latency_ms real
)"""

def init():
    if not settings.database_url:
        return 
    with psycopg.connect(settings.database_url) as conn:
        conn.execute(DDL)

def save_prediction(request_id, features, score, model_version, latency_ms):
    if not settings.database_url:
        return 
    with psycopg.connect(settings.database_url) as conn:
        conn.execute(
            "INSERT INTO predictions (request_id, model_version, features, score, latency_ms) "
            "VALUES (%s, %s, %s, %s, %s)",
            (request_id, model_version, features, score, latency_ms)
        )