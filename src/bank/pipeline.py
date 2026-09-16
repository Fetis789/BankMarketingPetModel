from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class CatBoostInferencePipeline:
    model: Any
    feature_names: list[str]
    categorical_features: list[str]
    numeric_features: list[str]
    numeric_medians: dict[str, float]

    def preprocess(self, X: pd.DataFrame | dict | list[dict]) -> pd.DataFrame:
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        elif isinstance(X, list):
            X = pd.DataFrame(X)
        else:
            X = X.copy()

        missing_features = set(self.feature_names) - set(X.columns)
        if missing_features:
            raise ValueError(f"Missing features: {sorted(missing_features)}")

        X = X[self.feature_names].copy()

        for feature in self.categorical_features:
            X[feature] = X[feature].fillna("__MISSING__").astype(str)

        for feature in self.numeric_features:
            X[feature] = pd.to_numeric(X[feature], errors="coerce")
            X[feature] = X[feature].fillna(self.numeric_medians[feature])

        return X

    def predict_proba(self, X: pd.DataFrame | dict | list[dict]) -> np.ndarray:
        return self.model.predict_proba(self.preprocess(X))