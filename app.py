import streamlit as st

st.set_page_config(
    page_title="PositionIQ",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        border: 1px solid rgba(130, 140, 160, 0.28);
        border-radius: 14px;
        padding: 0.9rem;
        background: rgba(255, 255, 255, 0.025);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.86rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.45rem;
    }

    .pi-hero {
        border: 1px solid rgba(130, 140, 160, 0.28);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.25rem;
        background: linear-gradient(
            135deg,
            rgba(60, 88, 255, 0.12),
            rgba(80, 200, 170, 0.06)
        );
    }

    .pi-kicker {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.78rem;
        opacity: 0.75;
        margin-bottom: 0.4rem;
    }

    .pi-hero h1 {
        margin: 0;
        font-size: 2.35rem;
        line-height: 1.1;
    }

    .pi-hero p {
        margin-top: 0.8rem;
        margin-bottom: 0;
        font-size: 1.05rem;
        opacity: 0.88;
        max-width: 780px;
    }

    .pi-card {
        border: 1px solid rgba(130, 140, 160, 0.28);
        border-radius: 16px;
        padding: 1.15rem;
        min-height: 190px;
        background: rgba(255, 255, 255, 0.02);
    }

    .pi-card h3 {
        margin: 0.4rem 0 0.55rem 0;
        font-size: 1.2rem;
        line-height: 1.25;
    }

    .pi-card p {
        margin: 0;
        opacity: 0.82;
        line-height: 1.5;
    }

    .pi-card .pi-icon {
        font-size: 1.6rem;
    }

    .pi-section-label {
        margin-top: 1rem;
        margin-bottom: 0.6rem;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        opacity: 0.7;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .pi-hero {
            padding: 1.35rem;
        }

        .pi-hero h1 {
            font-size: 1.8rem;
        }

        .pi-card {
            min-height: auto;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "experience_level" not in st.session_state:
    st.session_state.experience_level = "Beginner"

if "parlay_workspace" not in st.session_state:
    st.session_state.parlay_workspace = None

with st.sidebar:
    st.title("PositionIQ")
    st.caption("Understand every possible outcome.")

    st.radio(
        "Explanation level",
        ["Beginner", "Advanced"],
        key="experience_level",
        help=(
            "Beginner mode prioritizes interpretation and common mistakes. "
            "Advanced mode surfaces technical methodology and diagnostics."
        ),
    )

    if st.session_state.experience_level == "Beginner":
        st.info(
            "Beginner mode emphasizes plain-language explanations and "
            "practical takeaways."
        )
    else:
        st.info(
            "Advanced mode uses denser summaries and exposes methodology."
        )

    with st.expander("Sports betting glossary"):
        st.markdown(
            """
            **Implied probability:** Break-even win rate represented by odds.

            **Vig:** The sportsbook's built-in pricing advantage.

            **Overround:** The amount listed probabilities exceed 100%.

            **No-vig probability:** Market estimate after removing overround.

            **Expected value:** Modeled average profit or loss over time.

            **Hedge:** A second wager that changes the outcome distribution.

            **Cashout:** An offer to settle an open ticket early.

            **Correlation:** When one selection changes another's likelihood.

            **Total return:** Profit plus the returned original stake.
            """
        )

pages = {
    "Start": [
        st.Page(
            "positioniq_pages/home.py",
            title="Home",
            icon=":material/home:",
            default=True,
        ),
    ],
    "Core Bet Tools": [
        st.Page(
            "positioniq_pages/odds_converter.py",
            title="Odds Converter",
            icon=":material/swap_horiz:",
        ),
        st.Page(
            "positioniq_pages/no_vig.py",
            title="No-Vig Calculator",
            icon=":material/balance:",
        ),
        st.Page(
            "positioniq_pages/expected_value.py",
            title="EV Calculator",
            icon=":material/trending_up:",
        ),
    ],
    "Risk Management": [
        st.Page(
            "positioniq_pages/hedge.py",
            title="Hedge Calculator",
            icon=":material/shield:",
        ),
        st.Page(
            "positioniq_pages/cashout.py",
            title="Cashout Analyzer",
            icon=":material/paid:",
        ),
    ],
    "Parlays": [
        st.Page(
            "positioniq_pages/parlay_lab.py",
            title="Parlay Lab",
            icon=":material/account_tree:",
        ),
    ],
}

current_page = st.navigation(pages, position="sidebar")
current_page.run()

st.divider()
st.caption(
    "PositionIQ v1.0 — Modular multipage architecture with shared state, "
    "beginner and advanced explanations, and dedicated betting workflows."
)
