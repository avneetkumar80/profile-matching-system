"""Adaptive feedback-learning layer. Learns personalized feature weights per
user from their historical Accept/Reject feedback using logistic regression
over the three compatibility features (text, MBTI, location)."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from matching_engine import MatchingEngine, DEFAULT_WEIGHTS

MIN_FEEDBACK_FOR_LEARNING = 6
MIN_CLASS_COUNT = 2  # need at least this many accepts AND rejects to fit a model


@dataclass
class LearnedWeights:
    user_id: str
    weights: dict
    n_feedback: int
    used_fallback: bool


def _feature_rows_for_user(engine: MatchingEngine, feedback: pd.DataFrame, user_id: str) -> pd.DataFrame:
    user_feedback = feedback[feedback["user_id"] == user_id]
    rows = []
    for _, fb in user_feedback.iterrows():
        try:
            result = engine.calculate_compatibility(user_id, fb["matched_user_id"])
        except KeyError:
            continue
        rows.append({
            "text": result.text_score / 100.0,
            "mbti": result.mbti_score / 100.0,
            "location": result.location_score / 100.0,
            "action": fb["action"],
        })
    return pd.DataFrame(rows)


def learn_user_weights(engine: MatchingEngine, feedback: pd.DataFrame, user_id: str) -> LearnedWeights:
    data = _feature_rows_for_user(engine, feedback, user_id)
    n = len(data)

    if n < MIN_FEEDBACK_FOR_LEARNING or data["action"].nunique() < 2 or \
            data["action"].value_counts().min() < MIN_CLASS_COUNT:
        return LearnedWeights(user_id, dict(DEFAULT_WEIGHTS), n, used_fallback=True)

    X = data[["text", "mbti", "location"]].values
    y = data["action"].values

    model = LogisticRegression(max_iter=500, C=0.6)
    model.fit(X, y)

    raw_weights = np.clip(model.coef_[0], a_min=0, a_max=None)
    if raw_weights.sum() == 0:
        return LearnedWeights(user_id, dict(DEFAULT_WEIGHTS), n, used_fallback=True)

    normalized = raw_weights / raw_weights.sum()
    weights = {"text": float(normalized[0]), "mbti": float(normalized[1]), "location": float(normalized[2])}
    return LearnedWeights(user_id, weights, n, used_fallback=False)


def learn_all_user_weights(engine: MatchingEngine, feedback: pd.DataFrame, users: pd.DataFrame) -> dict:
    return {uid: learn_user_weights(engine, feedback, uid) for uid in users["user_id"]}
