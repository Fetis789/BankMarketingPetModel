import time
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

from bank import db
from bank.config import settings
from bank.model_store import load_model
from bank.service.preprocess import preprocess

PREDICTIONS = Counter("bank_predictions_total", "Predictions by class", ["response_flg"]) 
SCORE = Histogram("bank_score", "Predicted Response Probability", buckets=[i/10 for i in range(11)])
MODEL_INFO = Gauge("bank_model_info", "Model information", ["version"])
LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)


class Features(BaseModel):
    model_config = {"extra": "forbid"}

    euribor3m: float = Field(ge=0)
    nr_employed: float = Field(ge=0, alias="nr.employed")
    month: Literal["jan","feb","mar","apr","may","jun","jul","aug",
        "sep","oct","nov","dec"] = Field(description="Month of the last contact")
    campaign: int = Field(ge=0)
    job: str | None = None
    education: str
    age: int = Field(ge=0, le=120)
    emp_var_rate: float = Field(alias="emp.var.rate")
    cons_conf_idx: float = Field(alias="cons.conf.idx")
    day_of_week: Literal["mon","tue","wed","thu","fri","sat","sun"]


class Prediction(BaseModel):
    score: float
    response_flg: bool
    model_version: str
    request_id: str
    latency_ms: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline, app.state.meta, app.state.version = load_model()
    MODEL_INFO.labels(version=app.state.version).set(1)

    db.init()
    yield
    app.state.pipeline = None

app = FastAPI(title="bank-marketing-prediction", version="1.0.0", lifespan=lifespan)
Instrumentator().instrument(app, latency_lowr_buckets=LATENCY_BUCKETS).expose(app)

#Логирование ошибок при validation_error (неправильном вводе)
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    response = await request_validation_exception_handler(request, exc)

    if request.method == 'POST' and request.url.path == '/v1/predict':
        request_id = str(uuid.uuid4())
        ##Строка для интеграционного теста (найти request_id в таблице)
        response.headers["Request-ID"] = request_id

        raw_body = jsonable_encoder(exc.body)
        features = (
            raw_body
            if isinstance(raw_body, dict)
            else {"raw_body": raw_body}
        )

        tasks = BackgroundTasks()
        tasks.add_task(
            db.save_invalid_prediction, 
            request_id, 
            features, 
            getattr(app.state, "version", None), 
            response.status_code)
        response.background = tasks
    
    return response
   

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "model_version": getattr(app.state, "version", "unknown"),
        "model_path": str(settings.model_path)
    }

@app.get("/ready")
def ready():
    if getattr(app.state, "pipeline", None) is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}

@app.post("/v1/predict")
def predict(x: Features, bg: BackgroundTasks) -> Prediction:
    t0 = time.perf_counter()
    request_id = str(uuid.uuid4())

    payload = x.model_dump(by_alias=True)
    frame = preprocess(payload, app.state.meta)
    score = float(app.state.pipeline.predict_proba(frame)[0, 1])
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    bg.add_task(db.save_prediction, request_id, payload, score, app.state.version, latency_ms)

    response_flg = score >= app.state.meta["threshold"]
    PREDICTIONS.labels(response_flg=str(response_flg).lower()).inc()
    SCORE.observe(score)

    return Prediction(
            score=score, 
            response_flg=response_flg, 
            model_version=app.state.version, 
            request_id=request_id, 
            latency_ms=latency_ms
    )





    
