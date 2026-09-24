from typing import Any

import pandas as pd


def preprocess(
    payload: dict[str, Any],
    metadata: dict[str, Any],
) -> pd.DataFrame:
    
    feature_names = metadata["feature_names"]
    categorical_features = metadata["categorical_features"]
    numeric_features = metadata["numeric_features"]
    numeric_medians = metadata["numeric_medians"]

    frame = pd.DataFrame([payload])

    missing_features = set(feature_names) - set(frame.columns)

    if missing_features:
        raise ValueError(
            f"Missing required features: {sorted(missing_features)}"
        )

    # Оставляем только признаки модели в порядке обучения.
    frame = frame.reindex(columns=feature_names).copy()

    for feature in categorical_features:
        frame[feature] = (
            frame[feature]
            .fillna("__MISSING__")
            .astype(str)
        )

    for feature in numeric_features:
        frame[feature] = pd.to_numeric(
            frame[feature],
            errors="coerce",
        )
        frame[feature] = frame[feature].fillna(
            numeric_medians[feature]
        )

    return frame