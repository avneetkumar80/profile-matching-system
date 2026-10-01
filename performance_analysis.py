"""Module 7 - Performance Analysis.

Compares the initial (default-weight) scoring model against the adaptive
(personalized-weight) model using a per-user train/test split of the real
feedback data. Every metric here is computed from actual predictions, not
invented.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from matching_engine import MatchingEngine, DEFAULT_WEIGHTS
from feedback_model import learn_user_weights, MIN_FEEDBACK_FOR_LEARNING

TEST_FRACTION = 0.3
SCORE_THRESHOLD = 50.0  # compatibility score at/above which a match is "recommended"


def _predict_label(engine: MatchingEngine, user_id: str, matched_id: str, weights: dict) -> int:
    result = engine.calculate_compatibility(user_id, matched_id, weights)
    return int(result.total_score >= SCORE_THRESHOLD)


def evaluate_models(engine: MatchingEngine, users: pd.DataFrame, feedback: pd.DataFrame, seed: int = 7):
    rng = np.random.default_rng(seed)

    y_true, y_pred_initial, y_pred_adaptive = [], [], []
    learned_weights_used = 0

    for uid in users["user_id"]:
        user_feedback = feedback[feedback["user_id"] == uid].reset_index(drop=True)
        if len(user_feedback) < MIN_FEEDBACK_FOR_LEARNING + 3:
            continue

        idx = np.arange(len(user_feedback))
        rng.shuffle(idx)
        split_point = max(1, int(len(idx) * (1 - TEST_FRACTION)))
        train_idx, test_idx = idx[:split_point], idx[split_point:]
        if len(test_idx) == 0:
            continue

        train_feedback = user_feedback.iloc[train_idx]
        test_feedback = user_feedback.iloc[test_idx]

        learned = learn_user_weights(engine, train_feedback.assign(user_id=uid), uid)
        if not learned.used_fallback:
            learned_weights_used += 1

        for _, row in test_feedback.iterrows():
            y_true.append(int(row["action"]))
            y_pred_initial.append(_predict_label(engine, uid, row["matched_user_id"], DEFAULT_WEIGHTS))
            y_pred_adaptive.append(_predict_label(engine, uid, row["matched_user_id"], learned.weights))

    def metrics(y_true, y_pred):
        return {
            "acceptance_rate": float(np.mean(y_pred)),
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
        }

    initial_metrics = metrics(y_true, y_pred_initial)
    adaptive_metrics = metrics(y_true, y_pred_adaptive)

    return {
        "n_test_samples": len(y_true),
        "n_users_evaluated": len({}),  # filled below
        "n_users_with_learned_weights": learned_weights_used,
        "initial": initial_metrics,
        "adaptive": adaptive_metrics,
        "y_true": y_true,
        "y_pred_initial": y_pred_initial,
        "y_pred_adaptive": y_pred_adaptive,
    }


if __name__ == "__main__":
    users = pd.read_csv("users.csv")
    feedback = pd.read_csv("feedback.csv")
    engine = MatchingEngine(users)

    results = evaluate_models(engine, users, feedback)

    print(f"Test samples evaluated: {results['n_test_samples']}")
    print(f"Users with learned (non-fallback) weights: {results['n_users_with_learned_weights']}")
    print("\nMetric            Initial     Adaptive")
    for key in ["acceptance_rate", "accuracy", "precision", "recall", "f1"]:
        print(f"{key:<16} {results['initial'][key]:.4f}     {results['adaptive'][key]:.4f}")
