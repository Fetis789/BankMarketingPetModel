import pytest

from bank.service.app import app

def test_smoke(client, good_row):
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 < body['score'] < 1.0
    assert isinstance(body['response_flg'], bool)
    assert body['latency_ms'] > 0
    assert 'model_version' in body


def test_smoke_missing_job(client, good_row):
    bad_row = dict(good_row)
    bad_row['job'] = None
    r = client.post("/v1/predict", json=bad_row)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 < body['score'] < 1.0
    assert isinstance(body['response_flg'], bool)
    assert body['latency_ms'] > 0
    assert 'model_version' in body

def test_deterministic(client, good_row):
    r1 = client.post("/v1/predict", json=good_row)
    r2 = client.post("/v1/predict", json=good_row)
    assert r1.status_code == 200
    assert r2.status_code == 200
    s1 = r1.json()['score']
    s2 = r2.json()['score']
    assert abs(s1 - s2) < 1e-6

def test_smoke_model_version(client, good_row):
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    post_model_version = r.json()['model_version']
    r_health = client.get("/health")
    health_model_version = r_health.json()['model_version']
    assert post_model_version == health_model_version