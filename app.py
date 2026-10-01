"""Streamlit UI for the Intelligent Hybrid Profile-Based Matching and
Recommendation System."""

import pandas as pd
import streamlit as st

from matching_engine import MatchingEngine, DEFAULT_WEIGHTS
from feedback_model import learn_user_weights, MIN_FEEDBACK_FOR_LEARNING

USERS_PATH = "users.csv"
FEEDBACK_PATH = "feedback.csv"

st.set_page_config(page_title="Hybrid Matching System", page_icon="🤝", layout="wide")


@st.cache_resource
def load_engine():
    users = pd.read_csv(USERS_PATH)
    feedback = pd.read_csv(FEEDBACK_PATH)
    engine = MatchingEngine(users)
    return users, feedback, engine


def ensure_session_feedback(feedback: pd.DataFrame):
    if "session_feedback" not in st.session_state:
        st.session_state.session_feedback = feedback.copy()


def render_home():
    st.title("🤝 Intelligent Hybrid Profile-Based Matching System")
    st.markdown(
        "This system recommends compatible user profiles by combining three signals into a "
        "single compatibility score:"
    )
    c1, c2, c3 = st.columns(3)
    c1.info("**NLP Semantic Similarity**\n\nTF-IDF + cosine similarity over professional summary and about-me text.")
    c2.info("**MBTI Compatibility**\n\nRule-based scoring across shared and complementary personality traits.")
    c3.info("**Location Compatibility**\n\nSame city, same region, or different region scoring.")
    st.markdown(
        "Every time a user accepts or rejects a recommendation, the system records that feedback. "
        "Once enough feedback accumulates, a personalized logistic-regression model learns how much "
        "each of the three factors matters **to that specific user**, and future recommendations for "
        "them are re-weighted accordingly."
    )
    st.markdown("**Technologies used:** Python, Pandas, scikit-learn (TF-IDF, cosine similarity, "
                "Logistic Regression), Streamlit, Matplotlib.")


def render_user_selection(users: pd.DataFrame):
    st.header("👤 Select a Profile")
    options = users["user_id"] + " — " + users["name"]
    choice = st.selectbox("Choose a user", options)
    user_id = choice.split(" — ")[0]
    row = users.set_index("user_id").loc[user_id]

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Name", row["name"])
            st.metric("MBTI", row["mbti"])
            st.metric("Location", row["location"])
        with c2:
            st.markdown(f"**Professional Summary**\n\n{row['professional_summary']}")
            st.markdown(f"**About Me**\n\n{row['about_me']}")
    return user_id


def render_weights(user_id: str, engine: MatchingEngine, feedback: pd.DataFrame):
    st.subheader("⚖️ Personalized Weights")
    learned = learn_user_weights(engine, feedback, user_id)
    n = learned.weights
    if learned.used_fallback:
        st.warning(
            f"Insufficient feedback for personalization ({learned.n_feedback} interactions, "
            f"need at least {MIN_FEEDBACK_FOR_LEARNING}). Using default weights."
        )
    else:
        st.success(f"Personalized weights learned from {learned.n_feedback} feedback interactions.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Text / Professional", f"{n['text']*100:.1f}%")
    c2.metric("MBTI", f"{n['mbti']*100:.1f}%")
    c3.metric("Location", f"{n['location']*100:.1f}%")
    return learned.weights


def render_top_matches(user_id: str, users: pd.DataFrame, engine: MatchingEngine, weights: dict):
    st.header("🏆 Top 5 Matches")
    matches = engine.get_top_matches(user_id, top_n=5, weights=weights)
    users_indexed = users.set_index("user_id")

    for rank, m in enumerate(matches, start=1):
        row = users_indexed.loc[m.user_b]
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric(f"#{rank} {row['name']}", f"{m.total_score:.1f}%")
                st.caption(f"MBTI: {row['mbti']}  |  {row['location']}")
            with c2:
                st.write(f"*{m.explanation}*")
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("Text", f"{m.text_score:.0f}")
                sc2.metric("MBTI", f"{m.mbti_score:.0f}")
                sc3.metric("Location", f"{m.location_score:.0f}")
                with st.expander("View full profile"):
                    st.markdown(f"**Professional Summary:** {row['professional_summary']}")
                    st.markdown(f"**About Me:** {row['about_me']}")

            bcol1, bcol2, _ = st.columns([1, 1, 4])
            if bcol1.button("👍 Accept", key=f"accept_{m.user_b}"):
                record_feedback(user_id, m.user_b, 1)
                st.rerun()
            if bcol2.button("👎 Reject", key=f"reject_{m.user_b}"):
                record_feedback(user_id, m.user_b, 0)
                st.rerun()


def record_feedback(user_id: str, matched_id: str, action: int):
    ensure_session_feedback(st.session_state.get("_base_feedback", pd.DataFrame()))
    new_row = pd.DataFrame([{
        "user_id": user_id, "matched_user_id": matched_id, "action": action,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    st.session_state.session_feedback = pd.concat(
        [st.session_state.session_feedback, new_row], ignore_index=True
    )
    st.toast(f"Feedback recorded: {'Accepted' if action == 1 else 'Rejected'}.")


def main():
    users, base_feedback, engine = load_engine()
    st.session_state["_base_feedback"] = base_feedback
    ensure_session_feedback(base_feedback)
    feedback = st.session_state.session_feedback

    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Home", "Find Matches"], label_visibility="collapsed")
        st.caption(f"Dataset: {len(users)} users, {len(feedback)} feedback records (incl. session).")

    if page == "Home":
        render_home()
        return

    user_id = render_user_selection(users)
    st.divider()
    weights = render_weights(user_id, engine, feedback)
    st.divider()
    render_top_matches(user_id, users, engine, weights)


if __name__ == "__main__":
    main()
