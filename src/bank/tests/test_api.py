import numpy as np
import pytest

from bank.service.app import app

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert ('status', 'ok') in r.json().items()

def test_ready(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert ('status', 'ready') in r.json().items()


def test_predict_wrong_education_format(client, good_row):
    bad_row = good_row | {"education": 0}
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

def test_predict_missing_features(client, good_row):
    bad_row = dict(good_row)
    del bad_row["euribor3m"]
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

def test_predict_wrong_month_format(client, good_row):
    bad_row = good_row | {"month": "dan"}
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

def test_predict_wrong_day_of_week_format(client, good_row):
    bad_row = good_row | {"day_of_week": "unk"}
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

def test_predict_extra_features(client, good_row):
    bad_row = good_row | {"dop_not_need_filed": 2}
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

def test_predict_age_out_of_range(client, good_row):
    bad_row = good_row | {"age": -1}
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 422

@pytest.mark.parametrize(
    "score, threshold, expected", 
    [
        (0.3, 0.5, False),
        (0.7, 0.5, True),
        (1.0, 0.5, True),
    ]
)
def test_threshold_logic_check(client, good_row, monkeypatch, score, threshold, expected):
    monkeypatch.setattr(app.state.pipeline, "predict_proba", lambda x: np.array([[1 - score, score]]))
    monkeypatch.setitem(app.state.meta, "threshold", threshold)
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    body = r.json()
    assert body['response_flg'] == expected
    assert abs(body['score'] - score) < 1e-6


