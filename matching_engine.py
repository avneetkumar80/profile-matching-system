"""Core compatibility engine: NLP semantic similarity, MBTI compatibility,
location scoring, and the weighted aggregation formula."""

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "being", "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "that",
    "this", "these", "those", "it", "its", "their", "his", "her", "who", "which",
    "i", "me", "my", "you", "your", "we", "us", "our",
}

DEFAULT_WEIGHTS = {"text": 0.50, "mbti": 0.30, "location": 0.20}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


# --- MBTI compatibility -------------------------------------------------------
# Scoring reflects three factors: shared cognitive orientation (letters in
# common), a same-vs-complementary bonus for Judging/Perceiving pacing, and a
# communication-style adjustment for Thinking/Feeling pairs, which in practice
# tends to correlate with reported compatibility patterns.

def mbti_compatibility(mbti_a: str, mbti_b: str) -> float:
    if mbti_a == mbti_b:
        return 88.0  # identical types: strong shared understanding, some risk of blind spots

    shared_letters = sum(1 for x, y in zip(mbti_a, mbti_b) if x == y)
    base = 30 + shared_letters * 12  # 0 shared -> 30, 3 shared -> 66

    ei_a, ei_b = mbti_a[0], mbti_b[0]
    ns_a, ns_b = mbti_a[1], mbti_b[1]
    tf_a, tf_b = mbti_a[2], mbti_b[2]
    jp_a, jp_b = mbti_a[3], mbti_b[3]

    bonus = 0
    if ns_a == ns_b:
        bonus += 8  # shared information-processing style (Intuition/Sensing) aids mutual understanding
    if tf_a != tf_b:
        bonus += 6  # Thinking-Feeling complementarity often balances a partnership
    if jp_a == jp_b:
        bonus += 4  # similar pacing/structure preferences reduce friction
    if ei_a != ei_b:
        bonus += 4  # introvert-extrovert complementarity can balance social energy

    score = base + bonus
    return float(np.clip(score, 0, 100))


# --- Location compatibility ---------------------------------------------------

def location_compatibility(loc_a: str, loc_b: str) -> float:
    city_a, region_a = [p.strip() for p in loc_a.split(",")]
    city_b, region_b = [p.strip() for p in loc_b.split(",")]
    if city_a == city_b:
        return 100.0
    if region_a == region_b:
        return 60.0
    return 25.0


@dataclass
class CompatibilityResult:
    user_a: str
    user_b: str
    total_score: float
    text_score: float
    mbti_score: float
    location_score: float
    weights: dict
    explanation: str = ""


class MatchingEngine:
    def __init__(self, users: pd.DataFrame):
        self.users = users.set_index("user_id", drop=False)
        combined_text = (users["professional_summary"] + " " + users["about_me"]).apply(clean_text)
        self.vectorizer = TfidfVectorizer(max_features=2000)
        self.tfidf_matrix = self.vectorizer.fit_transform(combined_text)
        self.user_index = {uid: i for i, uid in enumerate(users["user_id"])}
        self._sim_cache = None

    def _text_similarity(self, user_a: str, user_b: str) -> float:
        if self._sim_cache is None:
            self._sim_cache = cosine_similarity(self.tfidf_matrix)
        i, j = self.user_index[user_a], self.user_index[user_b]
        return float(np.clip(self._sim_cache[i, j] * 100, 0, 100))

    def _explanation(self, text_s, mbti_s, loc_s, weights) -> str:
        contributions = {
            "professional/text alignment": weights["text"] * text_s,
            "MBTI compatibility": weights["mbti"] * mbti_s,
            "location proximity": weights["location"] * loc_s,
        }
        top_factor = max(contributions, key=contributions.get)
        if text_s >= 60:
            detail = "strong overlap in professional interests and personal values"
        elif mbti_s >= 70:
            detail = "a personality pairing that tends to communicate well"
        elif loc_s >= 60:
            detail = "geographic proximity"
        else:
            detail = "a moderate overall alignment across all factors"
        return f"Match driven primarily by {top_factor} ({detail})."

    def calculate_compatibility(self, user_a: str, user_b: str, weights: dict = None) -> CompatibilityResult:
        weights = weights or DEFAULT_WEIGHTS
        row_a, row_b = self.users.loc[user_a], self.users.loc[user_b]

        text_s = self._text_similarity(user_a, user_b)
        mbti_s = mbti_compatibility(row_a["mbti"], row_b["mbti"])
        loc_s = location_compatibility(row_a["location"], row_b["location"])

        total = weights["text"] * text_s + weights["mbti"] * mbti_s + weights["location"] * loc_s
        total = float(np.clip(total, 0, 100))

        explanation = self._explanation(text_s, mbti_s, loc_s, weights)

        return CompatibilityResult(user_a, user_b, total, text_s, mbti_s, loc_s, weights, explanation)

    def get_top_matches(self, user_id: str, top_n: int = 5, weights: dict = None):
        weights = weights or DEFAULT_WEIGHTS
        results = []
        for other_id in self.users["user_id"]:
            if other_id == user_id:
                continue
            results.append(self.calculate_compatibility(user_id, other_id, weights))
        results.sort(key=lambda r: r.total_score, reverse=True)
        return results[:top_n]
