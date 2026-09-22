import streamlit as st
import joblib

from models.predict import (
    rebuild_histories,
    build_features,
    MODEL_PATH,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VCT Match Predictor",
    page_icon="🎯",
    layout="wide",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at top left,
            #24113d 0%,
            #0b0b12 35%,
            #08080d 100%
        );
    color: white;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.main-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -2px;
    margin-top: 20px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #aaa8b5;
    font-size: 1.05rem;
    margin-bottom: 45px;
}

.team-label {
    color: #aaa8b5;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.vs {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 800;
    color: #8c7aff;
    padding-top: 30px;
}

.prediction-box {
    background: linear-gradient(
        135deg,
        rgba(124, 92, 255, 0.18),
        rgba(255, 255, 255, 0.035)
    );
    border: 1px solid rgba(140, 122, 255, 0.35);
    border-radius: 22px;
    padding: 30px;
    margin-top: 30px;
    text-align: center;
}

.prediction-label {
    color: #aaa8b5;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.8rem;
}

.prediction-winner {
    font-size: 2.5rem;
    font-weight: 800;
    margin-top: 8px;
}

.probability-card {
    background: rgba(255, 255, 255, 0.035);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 10px;
}

.probability-name {
    color: #aaa8b5;
    font-size: 0.9rem;
}

.probability-value {
    font-size: 2.2rem;
    font-weight: 800;
    margin-top: 5px;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 40px;
    margin-bottom: 15px;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3.2rem;
    font-size: 1.05rem;
    font-weight: 700;
    border: none;
    background: #7c5cff;
    color: white;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #9278ff;
    transform: translateY(-1px);
}

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.055);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.10);
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# LOAD MODEL + DATA
# =========================================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_resource
def load_histories():
    return rebuild_histories()


model = load_model()
histories, head_to_head = load_histories()

teams = sorted(histories.keys())


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎯 VCT MATCH PREDICTOR</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Machine learning powered Valorant match predictions'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# TEAM SELECTION
# =========================================================

col1, col2, col3 = st.columns([5, 1, 5])

with col1:

    st.markdown(
        '<div class="team-label">TEAM 1</div>',
        unsafe_allow_html=True,
    )

    team1 = st.selectbox(
        "Team 1",
        teams,
        label_visibility="collapsed",
    )


with col2:

    st.markdown(
        '<div class="vs">VS</div>',
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        '<div class="team-label">TEAM 2</div>',
        unsafe_allow_html=True,
    )

    team2 = st.selectbox(
        "Team 2",
        teams,
        index=1 if len(teams) > 1 else 0,
        label_visibility="collapsed",
    )


st.write("")


# =========================================================
# PREDICT BUTTON
# =========================================================

predict_clicked = st.button(
    "⚡ PREDICT MATCH",
    use_container_width=True,
)


# =========================================================
# PREDICTION
# =========================================================

if predict_clicked:

    if team1 == team2:

        st.error(
            "Please select two different teams."
        )

    else:

        X = build_features(
            team1,
            team2,
            histories,
            head_to_head,
        )

        prediction = model.predict(X)[0]

        probabilities = model.predict_proba(X)[0]

        team2_probability = probabilities[0]
        team1_probability = probabilities[1]

        predicted_winner = (
            team1
            if prediction == 1
            else team2
        )


        # =================================================
        # PREDICTED WINNER
        # =================================================

        st.markdown(
            f"""<div class="prediction-box">
<div class="prediction-label">MODEL PREDICTION</div>
<div class="prediction-winner">🏆 {predicted_winner}</div>
</div>""",
            unsafe_allow_html=True,
        )


        # =================================================
        # PROBABILITIES
        # =================================================

        st.markdown(
            '<div class="section-title">Win Probability</div>',
            unsafe_allow_html=True,
        )

        prob1, prob2 = st.columns(2)


        with prob1:

            st.markdown(
                f"""<div class="probability-card">
<div class="probability-name">{team1}</div>
<div class="probability-value">{team1_probability * 100:.1f}%</div>
</div>""",
                unsafe_allow_html=True,
            )

            st.progress(
                float(team1_probability)
            )


        with prob2:

            st.markdown(
                f"""<div class="probability-card">
<div class="probability-name">{team2}</div>
<div class="probability-value">{team2_probability * 100:.1f}%</div>
</div>""",
                unsafe_allow_html=True,
            )

            st.progress(
                float(team2_probability)
            )


        # =================================================
        # MATCH DATA
        # =================================================

        st.markdown(
            '<div class="section-title">Match Data</div>',
            unsafe_allow_html=True,
        )

        stat1, stat2, stat3 = st.columns(3)


        with stat1:

            st.metric(
                "Elo Difference",
                f"{X.iloc[0]['elo_diff']:.1f}",
            )


        with stat2:

            st.metric(
                "H2H Matches",
                int(X.iloc[0]["h2h_matches"]),
            )


        with stat3:

            st.metric(
                f"H2H Win Rate — {team1}",
                f"{X.iloc[0]['h2h_winrate'] * 100:.1f}%",
            )


        # =================================================
        # TEAM COMPARISON
        # =================================================

        st.markdown(
            '<div class="section-title">Team Comparison</div>',
            unsafe_allow_html=True,
        )

        comparison = {
            "Elo": (
                X.iloc[0]["team1_elo"],
                X.iloc[0]["team2_elo"],
            ),
            "Last 5 Win Rate": (
                X.iloc[0]["team1_last5_wr"] * 100,
                X.iloc[0]["team2_last5_wr"] * 100,
            ),
            "Average ACS": (
                X.iloc[0]["team1_avg_acs"],
                X.iloc[0]["team2_avg_acs"],
            ),
            "Average Rating": (
                X.iloc[0]["team1_avg_rating"],
                X.iloc[0]["team2_avg_rating"],
            ),
            "Average KAST": (
                X.iloc[0]["team1_avg_kast"],
                X.iloc[0]["team2_avg_kast"],
            ),
            "Average ADR": (
                X.iloc[0]["team1_avg_adr"],
                X.iloc[0]["team2_avg_adr"],
            ),
        }


        for stat_name, values in comparison.items():

            left, middle, right = st.columns([3, 2, 3])

            with left:

                st.markdown(
                    f"**{values[0]:.2f}**"
                )

            with middle:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        color:#aaa8b5;
                    ">
                        {stat_name}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with right:

                st.markdown(
                    f"""
                    <div style="
                        text-align:right;
                    ">
                        <b>{values[1]:.2f}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <br><br>

    <div style="
        text-align:center;
        color:#66636f;
        font-size:0.8rem;
    ">
        VCT Match Predictor • Random Forest ML Model
    </div>
    """,
    unsafe_allow_html=True,
)