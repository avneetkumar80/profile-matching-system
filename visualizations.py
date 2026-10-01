"""Module 10 - Visualizations. Generates all charts from the actual generated
data and evaluation results, saved as PNG files."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matching_engine import MatchingEngine, DEFAULT_WEIGHTS
from feedback_model import learn_all_user_weights
from performance_analysis import evaluate_models

plt.rcParams["figure.dpi"] = 150


def plot_mbti_distribution(users: pd.DataFrame, path="viz_mbti_distribution.png"):
    counts = users["mbti"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(counts.index, counts.values, color="#2f5597")
    ax.set_title("Distribution of MBTI Types Across Users")
    ax.set_xlabel("MBTI Type")
    ax.set_ylabel("Number of Users")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_location_distribution(users: pd.DataFrame, path="viz_location_distribution.png"):
    cities = users["location"].apply(lambda x: x.split(",")[0].strip()).value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(cities.index[::-1], cities.values[::-1], color="#548235")
    ax.set_title("User Distribution by City")
    ax.set_xlabel("Number of Users")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_compatibility_distribution(engine: MatchingEngine, users: pd.DataFrame, path="viz_compat_distribution.png", n_pairs=1500):
    rng = np.random.default_rng(11)
    ids = users["user_id"].values
    scores = []
    for _ in range(n_pairs):
        a, b = rng.choice(ids, size=2, replace=False)
        scores.append(engine.calculate_compatibility(a, b).total_score)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(scores, bins=30, color="#7030a0", edgecolor="white")
    ax.set_title(f"Distribution of Compatibility Scores ({n_pairs} Random User Pairs)")
    ax.set_xlabel("Compatibility Score (%)")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return scores


def plot_model_comparison(results: dict, path="viz_model_comparison.png"):
    metrics = ["accuracy", "precision", "recall", "f1"]
    initial_vals = [results["initial"][m] for m in metrics]
    adaptive_vals = [results["adaptive"][m] for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - width / 2, initial_vals, width, label="Initial Model", color="#a6a6a6")
    ax.bar(x + width / 2, adaptive_vals, width, label="Adaptive Model", color="#2f5597")
    ax.set_xticks(x)
    ax.set_xticklabels([m.capitalize() for m in metrics])
    ax.set_ylim(0, 1)
    ax.set_title("Initial vs Adaptive Model Performance")
    ax.legend()
    for i, v in enumerate(initial_vals):
        ax.text(i - width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    for i, v in enumerate(adaptive_vals):
        ax.text(i + width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_weight_comparison(learned_weights: dict, path="viz_weight_comparison.png"):
    personalized = [lw for lw in learned_weights.values() if not lw.used_fallback]
    avg_text = np.mean([lw.weights["text"] for lw in personalized])
    avg_mbti = np.mean([lw.weights["mbti"] for lw in personalized])
    avg_location = np.mean([lw.weights["location"] for lw in personalized])

    labels = ["Text/Professional", "MBTI", "Location"]
    initial = [DEFAULT_WEIGHTS["text"], DEFAULT_WEIGHTS["mbti"], DEFAULT_WEIGHTS["location"]]
    adaptive_avg = [avg_text, avg_mbti, avg_location]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(x - width / 2, initial, width, label="Initial (Default) Weights", color="#a6a6a6")
    ax.bar(x + width / 2, adaptive_avg, width, label="Average Learned Weights", color="#c55a11")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Weight")
    ax.set_title("Default vs Average Personalized Feature Weights")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return {"text": avg_text, "mbti": avg_mbti, "location": avg_location}


def plot_feedback_distribution(feedback: pd.DataFrame, path="viz_feedback_distribution.png"):
    counts = feedback["action"].value_counts().sort_index()
    labels = ["Reject (0)", "Accept (1)"]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.bar(labels, [counts.get(0, 0), counts.get(1, 0)], color=["#c00000", "#548235"])
    ax.set_title("Feedback Accept / Reject Distribution")
    ax.set_ylabel("Count")
    for i, v in enumerate([counts.get(0, 0), counts.get(1, 0)]):
        ax.text(i, v + 5, str(v), ha="center")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    users = pd.read_csv("users.csv")
    feedback = pd.read_csv("feedback.csv")
    engine = MatchingEngine(users)

    plot_mbti_distribution(users)
    plot_location_distribution(users)
    plot_compatibility_distribution(engine, users)
    plot_feedback_distribution(feedback)

    results = evaluate_models(engine, users, feedback)
    plot_model_comparison(results)

    learned_weights = learn_all_user_weights(engine, feedback, users)
    avg_weights = plot_weight_comparison(learned_weights)

    print("All visualizations saved.")
    print("Average personalized weights:", {k: round(v, 3) for k, v in avg_weights.items()})
