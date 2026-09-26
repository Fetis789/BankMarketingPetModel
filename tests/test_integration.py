import os

import psycopg
import pytest

from bank.service.app import app

DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not DATABASE_URL, reason="нужна база данных Postgres: задайте DATABASE_URL"),
]

def test_prediction_is_logged(client, good_row):
    r = client.post("/v1/predict", json=good_row).json()

    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "SELECT model_version, score, features->>'month', status_code "
            "FROM predictions WHERE request_id = %s",
            (r["request_id"],),
        ).fetchone()
    
    assert row is not None
    assert row[0] == r["model_version"]
    assert row[1] == pytest.approx(r["score"])
    assert row[2] == good_row["month"]
    assert row[3] == 200


def test_prediction_is_logged_bad_row(client, bad_row):
    r = client.post("/v1/predict", json=bad_row)

    assert r.status_code == 422

    request_id = r.headers["Request-ID"]

    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "SELECT model_version, score, features->>'month', status_code "
            "FROM predictions WHERE request_id = %s",
            (request_id,),
        ).fetchone()
    
    assert row is not None
    assert row[0] == app.state.version
    assert row[1] is None
    assert row[3] == 422
