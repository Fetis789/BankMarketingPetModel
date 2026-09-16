import time
import uuid

from contextlib import contextmanager

import joblib 
import pandas as pd

from fastapi import FastAPI, HTTPException, BackgroundTasks

from pydantic import BaseModel, Field

from churn import db
from churn.config import settings

class Features(BaseModel):
    model_config = {"extra": "forbid"}

    euribor3m: float = Field(ge=0, description="EURIBOR 3M rate")
    nr.employeed: float = Field(ge=0, description="Number of employed")
    month: Literal["jan","feb","mar","apr","may","jun","jul","aug",
        "sep", "oct","nov","dec"] = Field(description="Month of the last contact")
    
