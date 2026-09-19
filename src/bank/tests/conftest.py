import pytest
from fastapi.testclient import TestClient

from bank.service.app import app

@pytest.fixture(scope ="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def good_row():
    return {
        "euribor3m": 4.857,
        "nr.employed": 5191.0,
        "month": "may",
        "campaign": 2,
        "job": "technician",
        "education": "professional.course",
        "age": 42,
        "emp.var.rate": -1.8,
        "cons.conf.idx": -46.2,
        "day_of_week": "mon"
        }

