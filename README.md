# Intelligent Hybrid Profile-Based Matching and Recommendation System

A Python-based recommendation engine that scores compatibility between user
profiles by combining semantic text similarity, MBTI personality
compatibility, and location proximity — then personalizes those scores over
time using feedback-driven adaptive learning.

## Features

- Synthetic but realistic dataset of 120 user profiles and 2,400+ feedback interactions
- TF-IDF + cosine similarity semantic matching over profile text
- Explainable, rule-based MBTI compatibility scoring
- Deterministic location scoring (same city / same region / different region)
- Weighted compatibility engine producing a single 0–100% score
- Adaptive per-user weight learning via logistic regression on Accept/Reject feedback
- Top-5 recommendation engine with human-readable match explanations
- Interactive Streamlit application with live feedback collection
- Full performance evaluation comparing the default and personalized models

## Architecture

```
User Profiles → Preprocessing → NLP Semantic Analysis ─┐
                                  MBTI Compatibility ───┼→ Weighted Compatibility Engine → Top-5 Recommendations
                                  Location Scoring ──────┘                                        ↓
                                                                                              User Feedback
                                                                                                    ↓
                                                                                            Adaptive Learning
                                                                                                    ↓
                                                                                          Personalized Weights
                                                                                                    ↓
                                                                                          Improved Recommendations
```

## Technologies

Python, Pandas, NumPy, scikit-learn (TF-IDF, cosine similarity, Logistic
Regression), Streamlit, Matplotlib.

## Files

| File | Purpose |
|---|---|
| `generate_dataset.py` | Generates `users.csv` and `feedback.csv`, validates them |
| `matching_engine.py` | TF-IDF similarity, MBTI/location scoring, compatibility formula, top-N recommendations |
| `feedback_model.py` | Adaptive per-user weight learning (logistic regression) |
| `performance_analysis.py` | Initial vs adaptive model evaluation on held-out feedback |
| `visualizations.py` | Generates all charts used in this README and the report |
| `app.py` | Streamlit application |
| `users.csv` / `feedback.csv` | Generated datasets |

## Dataset

`users.csv` (120 rows): `user_id, name, age, gender, location, mbti,
professional_summary, about_me`. Text fields are generated from
MBTI-conditioned templates (industry, skills, traits, values, interests) so
profiles read naturally and are internally consistent rather than random.

`feedback.csv` (2,479 rows): `user_id, matched_user_id, action, timestamp`.
Each user is assigned a hidden behavioral archetype (text-driven,
MBTI-driven, location-driven, or balanced) that shapes their accept/reject
probabilities, so the adaptive model has real signal to recover.

## Matching Methodology

```
TotalScore = 0.50 × TextSimilarity + 0.30 × MBTICompatibility + 0.20 × LocationScore
```

Initial weights reflect the assumption that professional/personal
compatibility (text) is the strongest general predictor of a good match,
followed by personality compatibility, with location as a supporting factor.
All three sub-scores are normalized to 0–100 before weighting.

## Adaptive Feedback Mechanism

For each user with sufficient feedback (≥6 interactions, with both accepted
and rejected examples), a logistic regression model is fit on that user's
historical (text, MBTI, location) scores against their accept/reject labels.
The resulting coefficients are clipped to non-negative values and normalized
to sum to 1, producing a personalized weight vector. Users with insufficient
feedback fall back to the default weights, and the UI clearly indicates when
this is happening.

## Installation

```bash
pip install pandas numpy scikit-learn streamlit matplotlib
```

## How to Run

```bash
python generate_dataset.py     # generates users.csv and feedback.csv
python performance_analysis.py # prints initial vs adaptive metrics
python visualizations.py       # saves all chart PNGs
streamlit run app.py           # launches the interactive app
```

## Example Usage

```python
from matching_engine import MatchingEngine
import pandas as pd

users = pd.read_csv("users.csv")
engine = MatchingEngine(users)

result = engine.calculate_compatibility("U0001", "U0002")
print(result.total_score, result.explanation)

top5 = engine.get_top_matches("U0001", top_n=5)
```

## Results

On held-out feedback (30% per-user test split), the adaptive model improved
F1 from 0.16 to 0.41 and recall from 0.10 to 0.38 relative to the default
weighting, at a small cost to raw accuracy (0.69 → 0.67) — the personalized
model recommends more matches overall and captures substantially more of
each user's genuine preferences. See `report.pdf` for full metrics and
charts.

## Limitations

- Feedback and profiles are synthetically generated; real-world text and
  behavior are noisier and less structured.
- TF-IDF captures lexical overlap, not deep semantic meaning — two profiles
  describing similar ideas in very different words will score lower than
  they conceptually should.
- Per-user logistic regression on ~15–25 feedback points is inherently
  noisy; some users' learned weights do not cleanly match their underlying
  behavioral archetype.
- MBTI compatibility scoring is a simplified heuristic, not a validated
  psychological instrument.
- Cold-start users (little to no feedback) always fall back to default
  weights until enough signal accumulates.

## Future Improvements

- Replace TF-IDF with Sentence-Transformer/BERT embeddings for true semantic matching
- Add collaborative filtering signals alongside content-based scoring
- Explore a hybrid neural recommendation architecture
- Model feedback recency/decay instead of treating all history equally
- Add real-time incremental learning instead of batch refitting
- Incorporate explainable-AI techniques (e.g. SHAP) for richer match explanations
- Validate against real user data at larger scale
