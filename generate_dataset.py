"""Synthetic dataset generation for the matching system: users.csv and feedback.csv."""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RNG_SEED = 42

MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
]

# Each MBTI type is loosely associated with an industry cluster and work-style
# language, so generated text is not random relative to the assigned type.
MBTI_PROFILE_BIAS = {
    "INTJ": {"industries": ["data science", "software architecture", "strategy consulting"], "traits": ["independent", "analytical", "long-term planner"]},
    "INTP": {"industries": ["machine learning research", "software engineering", "academia"], "traits": ["curious", "logical", "idea-driven"]},
    "ENTJ": {"industries": ["management consulting", "business strategy", "product leadership"], "traits": ["decisive", "goal-oriented", "confident"]},
    "ENTP": {"industries": ["startups", "product design", "venture building"], "traits": ["inventive", "debate-loving", "adaptable"]},
    "INFJ": {"industries": ["UX research", "counseling", "non-profit strategy"], "traits": ["empathetic", "idealistic", "insightful"]},
    "INFP": {"industries": ["content design", "creative writing", "social impact"], "traits": ["values-driven", "imaginative", "reflective"]},
    "ENFJ": {"industries": ["people operations", "community management", "education"], "traits": ["encouraging", "people-focused", "organized"]},
    "ENFP": {"industries": ["marketing", "brand strategy", "public relations"], "traits": ["enthusiastic", "expressive", "spontaneous"]},
    "ISTJ": {"industries": ["finance", "operations", "quality assurance"], "traits": ["dependable", "methodical", "detail-oriented"]},
    "ISFJ": {"industries": ["healthcare administration", "customer support", "HR"], "traits": ["supportive", "conscientious", "steady"]},
    "ESTJ": {"industries": ["project management", "logistics", "operations management"], "traits": ["organized", "practical", "results-driven"]},
    "ESFJ": {"industries": ["event management", "sales", "client relations"], "traits": ["sociable", "cooperative", "reliable"]},
    "ISTP": {"industries": ["systems engineering", "DevOps", "hardware design"], "traits": ["hands-on", "pragmatic", "calm under pressure"]},
    "ISFP": {"industries": ["graphic design", "UI design", "photography"], "traits": ["artistic", "gentle", "detail-aware"]},
    "ESTP": {"industries": ["sales", "business development", "trading"], "traits": ["energetic", "action-oriented", "persuasive"]},
    "ESFP": {"industries": ["marketing", "hospitality", "talent management"], "traits": ["outgoing", "warm", "spontaneous"]},
}

SKILLS_POOL = [
    "Python", "SQL", "data visualization", "machine learning", "cloud infrastructure",
    "product management", "UX research", "financial modeling", "digital marketing",
    "public speaking", "negotiation", "project planning", "statistical analysis",
    "content strategy", "customer discovery", "team leadership", "process optimization",
    "graphic design", "copywriting", "business development", "agile methodologies",
]

CAREER_GOALS = [
    "building data-driven products that solve real business problems",
    "growing into a leadership role while mentoring junior teammates",
    "transitioning into a more strategic, cross-functional position",
    "deepening technical expertise in a specialized domain",
    "starting an independent venture within the next few years",
    "working on socially impactful projects with measurable outcomes",
    "becoming a recognized expert in a fast-growing industry niche",
    "balancing hands-on execution with long-term strategic thinking",
]

VALUES_POOL = [
    "continuous learning", "honest communication", "work-life balance",
    "collaborative teamwork", "intellectual curiosity", "accountability",
    "creativity", "inclusivity", "efficiency", "empathy", "integrity",
    "innovation",
]

INTERESTS_POOL = [
    "hiking", "reading non-fiction", "cooking", "chess", "photography",
    "running", "traveling", "playing guitar", "board games", "yoga",
    "cycling", "painting", "podcasts about technology", "volunteering",
    "gardening", "film", "writing", "badminton",
]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Kabir", "Dev", "Ananya", "Diya", "Saanvi", "Aadhya",
    "Myra", "Isha", "Riya", "Anika", "Meera", "Kiara", "Priya", "Neha",
    "Rahul", "Karan", "Nikhil", "Varun", "Sanjay", "Amit", "Pooja", "Sneha",
    "Divya", "Aisha", "Farah", "Zoya", "Liam", "Noah", "Emma", "Olivia",
    "Ava", "Sophia", "Ethan", "Mason", "Lucas", "Mia", "Amelia", "Harper",
    "Daniel", "Ryan",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Iyer", "Nair", "Reddy", "Rao", "Menon",
    "Kapoor", "Malhotra", "Chatterjee", "Bose", "Mukherjee", "Pillai",
    "Khan", "Ahmed", "Patel", "Shah", "Joshi", "Desai", "Kulkarni",
    "Singh", "Kumar", "Das", "Sen", "Roy", "Chowdhury", "Bhatt",
    "Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson",
]

CITIES = {
    "Bangalore": "Karnataka", "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    "Chennai": "Tamil Nadu", "Vellore": "Tamil Nadu", "Coimbatore": "Tamil Nadu",
    "Hyderabad": "Telangana", "Delhi": "Delhi NCR", "Gurgaon": "Delhi NCR",
    "Noida": "Delhi NCR", "Kolkata": "West Bengal", "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan", "Kochi": "Kerala", "Chandigarh": "Punjab",
}


def _mbti_gender_age(rng: random.Random):
    return rng.choice(["Male", "Female", "Non-binary"]), rng.randint(21, 38)


def _professional_summary(rng: random.Random, mbti: str, skills: list) -> str:
    bias = MBTI_PROFILE_BIAS[mbti]
    industry = rng.choice(bias["industries"])
    goal = rng.choice(CAREER_GOALS)
    templates = [
        f"Professional with a background in {industry}, skilled in {skills[0]}, {skills[1]}, and {skills[2]}. "
        f"Currently focused on {goal}.",
        f"Works in {industry} with hands-on experience in {skills[0]} and {skills[1]}. "
        f"Interested in {goal}, and enjoys applying {skills[2]} to real-world problems.",
        f"Background spans {industry}, with core strengths in {skills[0]}, {skills[1]}, and {skills[2]}. "
        f"Actively working toward {goal}.",
    ]
    return rng.choice(templates)


def _about_me(rng: random.Random, mbti: str) -> str:
    bias = MBTI_PROFILE_BIAS[mbti]
    traits = rng.sample(bias["traits"], k=2)
    values = rng.sample(VALUES_POOL, k=2)
    interests = rng.sample(INTERESTS_POOL, k=2)
    templates = [
        f"Generally described as {traits[0]} and {traits[1]}. Values {values[0]} and {values[1]} "
        f"in both work and personal life. Enjoys {interests[0]} and {interests[1]} outside of work.",
        f"Tends to be {traits[0]}, with a {traits[1]} approach to problem-solving. "
        f"Cares deeply about {values[0]}, and unwinds with {interests[0]} or {interests[1]}.",
        f"A {traits[0]}, {traits[1]} personality who prioritizes {values[0]} and {values[1]}. "
        f"Free time usually goes toward {interests[0]} or exploring {interests[1]}.",
    ]
    return rng.choice(templates)


def generate_users(n: int = 120, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    used_names = set()
    for i in range(1, n + 1):
        while True:
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            if name not in used_names:
                used_names.add(name)
                break
        gender, age = _mbti_gender_age(rng)
        mbti = rng.choice(MBTI_TYPES)
        city = rng.choice(list(CITIES.keys()))
        skills = rng.sample(SKILLS_POOL, k=4)
        rows.append({
            "user_id": f"U{i:04d}",
            "name": name,
            "age": age,
            "gender": gender,
            "location": f"{city}, {CITIES[city]}",
            "mbti": mbti,
            "professional_summary": _professional_summary(rng, mbti, skills),
            "about_me": _about_me(rng, mbti),
        })
    return pd.DataFrame(rows)


# --- Feedback generation with per-user behavioral bias -----------------------

FEEDBACK_ARCHETYPES = ["text_driven", "mbti_driven", "location_driven", "balanced"]


def _assign_archetype(rng: random.Random) -> str:
    return rng.choices(FEEDBACK_ARCHETYPES, weights=[0.35, 0.25, 0.15, 0.25], k=1)[0]


def _text_similarity_quick(a: str, b: str) -> float:
    set_a, set_b = set(a.lower().split()), set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


MBTI_GROUP = {  # simplified group used only for synthetic feedback bias, not the real scoring engine
    t: t[1] + t[2] for t in MBTI_TYPES  # e.g. NT, NF, SJ, SP style pairing signal
}


def generate_feedback(users: pd.DataFrame, min_per_user: int = 15, max_per_user: int = 26,
                       seed: int = RNG_SEED) -> pd.DataFrame:
    rng = random.Random(seed + 1)
    np_rng = np.random.default_rng(seed + 1)

    archetypes = {uid: _assign_archetype(rng) for uid in users["user_id"]}
    users_indexed = users.set_index("user_id")

    start_time = datetime(2026, 1, 1)
    rows = []
    seen_pairs = set()

    for uid in users["user_id"]:
        n_interactions = rng.randint(min_per_user, max_per_user)
        candidates = [c for c in users["user_id"] if c != uid]
        targets = rng.sample(candidates, k=min(n_interactions, len(candidates)))
        archetype = archetypes[uid]
        u_row = users_indexed.loc[uid]

        for t_uid in targets:
            pair_key = (uid, t_uid)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            t_row = users_indexed.loc[t_uid]

            text_sim = _text_similarity_quick(
                u_row["professional_summary"] + " " + u_row["about_me"],
                t_row["professional_summary"] + " " + t_row["about_me"],
            )
            same_mbti_group = MBTI_GROUP[u_row["mbti"]] == MBTI_GROUP[t_row["mbti"]]
            same_location = u_row["location"].split(",")[1].strip() == t_row["location"].split(",")[1].strip()

            # Base acceptance probability shaped by the user's archetype so that
            # a learning model can recover a meaningful, distinguishable signal.
            if archetype == "text_driven":
                prob = 0.08 + 0.85 * text_sim
            elif archetype == "mbti_driven":
                prob = 0.82 if same_mbti_group else 0.12
            elif archetype == "location_driven":
                prob = 0.80 if same_location else 0.15
            else:  # balanced
                prob = 0.20 + 0.40 * text_sim + (0.25 if same_mbti_group else 0) + (0.20 if same_location else 0)

            prob = float(np.clip(prob + np_rng.normal(0, 0.05), 0.02, 0.98))
            action = int(np_rng.random() < prob)

            timestamp = start_time + timedelta(
                days=int(rng.randint(0, 200)), hours=int(rng.randint(0, 23)), minutes=int(rng.randint(0, 59))
            )
            rows.append({
                "user_id": uid,
                "matched_user_id": t_uid,
                "action": action,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            })

    df = pd.DataFrame(rows)
    return df, archetypes


def validate_datasets(users: pd.DataFrame, feedback: pd.DataFrame) -> dict:
    issues = []

    if users["user_id"].duplicated().any():
        issues.append("Duplicate user_id found in users.csv")
    if users.isnull().any().any():
        issues.append("Empty fields found in users.csv")
    invalid_mbti = ~users["mbti"].isin(MBTI_TYPES)
    if invalid_mbti.any():
        issues.append(f"{invalid_mbti.sum()} invalid MBTI values found")
    if (users["professional_summary"].str.len() < 20).any():
        issues.append("Some professional_summary entries are too short / low quality")
    if (users["about_me"].str.len() < 20).any():
        issues.append("Some about_me entries are too short / low quality")

    if feedback.duplicated(subset=["user_id", "matched_user_id"]).any():
        issues.append("Duplicate feedback rows found")
    if feedback.isnull().any().any():
        issues.append("Empty fields found in feedback.csv")
    if not feedback["action"].isin([0, 1]).all():
        issues.append("Invalid action values found in feedback.csv (must be 0 or 1)")
    valid_ids = set(users["user_id"])
    if not feedback["user_id"].isin(valid_ids).all() or not feedback["matched_user_id"].isin(valid_ids).all():
        issues.append("feedback.csv references user_id(s) not present in users.csv")
    try:
        pd.to_datetime(feedback["timestamp"])
    except Exception:
        issues.append("Invalid timestamp format found in feedback.csv")

    return {"valid": len(issues) == 0, "issues": issues}


if __name__ == "__main__":
    users_df = generate_users(n=120)
    feedback_df, archetypes = generate_feedback(users_df)

    report = validate_datasets(users_df, feedback_df)
    print("Validation:", "PASSED" if report["valid"] else "FAILED")
    for issue in report["issues"]:
        print(" -", issue)

    users_df.to_csv("users.csv", index=False)
    feedback_df.to_csv("feedback.csv", index=False)

    pd.DataFrame({"user_id": list(archetypes.keys()), "archetype": list(archetypes.values())}) \
        .to_csv("archetypes_debug.csv", index=False)

    print(f"users.csv: {len(users_df)} rows")
    print(f"feedback.csv: {len(feedback_df)} rows")
    print("MBTI distribution:\n", users_df["mbti"].value_counts())
    print("Action distribution:\n", feedback_df["action"].value_counts())
