import time
import uuid

from contextlib import contextmanager

import joblib 
import pandas as pd

from fastapi import FastAPI, HTTPException, BackgroundTasks

from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

from churn import db
from churn.config import settings

class Features(BaseModel):
    model_config = {"extra": "forbid"}

    euribor3m: float = Field(ge=0)
    nr.employeed: float = Field(ge=0)
    month: Literal["jan","feb","mar","apr","may","jun","jul","aug",
        "sep","oct","nov","dec"] = Field(description="Month of the last contact")
    campaign: int = Field(ge=0)
    job: str
    education: str
    age: int = Field(ge=0)
    emp.var.rate: float = Field(description="Employment variation rate")
    cons.conf.idx: float
    day_of_week: Literal["mon","tue","wed","thu","fri","sat","sun"]


class Prediction(BaseModel):
    score: float
    app: bool
    model_version: str
    request_id: str
    latency_ms: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    bundle = joblib.load(settings.MODEL_PATH)
    app.state.pipeline = bundle["pipeline"]
    app.state.meta = bundle["metadata"]
    app.state.version = bundle["metadata"]["model_version"]

    db.init()
    yield
    app.state.pipeline = None

app = FastAPI(title="bank-marketing-prediction", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok", "model_version": getattr(app.state, "version", "unknown")}

@app.get("/ready"):
    





    
