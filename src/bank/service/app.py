import time
import uuid

from contextlib import contextmanager

import joblib 
import pandas as pd

from fastapi import FastAPI, HTTPException, BackgroundTasks

from pydantic import BaseModel, Field

from churn import db
from churn.config import settings

class Features