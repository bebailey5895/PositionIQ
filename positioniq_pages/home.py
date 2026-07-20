import streamlit as st

from positioniq_components.ui import get_experience_level


experience_level = get_experience_level()

st.markdown(
    """
    <style>
    .home-hero {
        border: 1px solid rgba(130, 140, 160, 0.28);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(
            135deg,
            rgba(60, 88, 255, 0.14),
            rgba(80, 200, 170, 0.07)
        );
    }

    .home-kicker {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.78rem;
        opacity: 0.75;
        margin-bottom: 0.5rem;
    }

    .home-hero h1 {
        margin: 0;
        font-size: 2.35rem;
        line-height: 1.12;
    }

    .home-hero p {
        margin-top: 0.9rem;
        margin-bottom: 0;
        font-size: 1.05rem;
        opacity: 0.88;
        max-width: 790px;
    }

    .tool-card-content {
        min-height: 132px;
    }

    .tool-card-icon {
        font-size: 1.45rem;
        margin-bottom: 0.45rem;
    }

    .tool-card-content h3 {
        font-size: 1.06rem;
        line-height: 1.25;
        margin: 0 0 0.5rem 0;
    }

    .tool-card-content p {
        line-height: 1.42;
        margin: 0;
        opacity: 0.82;
        font-size: 0.92rem;
    }

    div[data-testid="stPageLink"] a {
        width: 100%;
        justify-content: center;
        border: 1px solid rgba(130, 140, 160, 0.30);
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        text-decoration: none;
    }

    div[data-testid="stPageLink"] a:hover {
        border-color: rgba(90, 145, 255, 0.85);
        background: rgba(60, 88, 255, 0.08);
    }

    @media (max-width: 760px) {
        .home-hero {
            padding: 1.35rem;
        }

        .home-hero h1 {
            font-size: 1.8rem;
        }

        .tool-card-content {
            min-height: auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-hero">
        <div class="home-kicker">Sports betting decision tools</div>
        <h1>Understand the price, risk, and trade-off before you act.</h1>
        <p>
            PositionIQ turns sportsbook odds, parlays, hedges, cashouts,
            and line movement into explanations that make sense for both
            new and experienced bettors.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

workspace = st.session_state.get("parlay_workspace")

if workspace:
    with st.container(border=True):
        resume_col1, resume_col2 = st.columns([3, 1])

        with resume_col1:
            st.markdown("#### Resume your saved parlay")
            st.write(
                f"**{workspace['ticket_name']}** · "
                f"{workspace['event_count']} events · "
                f"{workspace['total_selections']} selections"
            )
            st.caption(
                f"Stake: ${workspace['stake']:,.2f} · "
                f"Original odds: {workspace['offered_american']:+.0f} · "
                f"Potential payout: ${workspace['offered_total_return']:,.2f}"
            )

        with resume_col2:
            st.page_link(
                "positioniq_pages/parlay_lab.py",
                label="Open Parlay Lab",
                icon=":material/arrow_forward:",
                use_container_width=True,
            )

st.markdown("### Choose what you are trying to do")
st.caption("Open the tool that matches your decision.")


def tool_card(
    icon: str,
    title: str,
    description: str,
    page: str,
    button_label: str,
    material_icon: str,
) -> None:
    """Render a uniform interactive tool card."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="tool-card-content">
                <div class="tool-card-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link(
            page,
            label=button_label,
            icon=material_icon,
            use_container_width=True,
        )


row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    tool_card(
        "🔄",
        "Understand the odds",
        "Convert odds formats and see profit, total return, and break-even rate.",
        "positioniq_pages/odds_converter.py",
        "Open Odds Converter",
        ":material/swap_horiz:",
    )

with row1_col2:
    tool_card(
        "⚖️",
        "Estimate market probability",
        "Remove estimated margin from a complete two-way or three-way market.",
        "positioniq_pages/no_vig.py",
        "Open No-Vig Calculator",
        ":material/balance:",
    )

with row1_col3:
    tool_card(
        "📈",
        "Evaluate a price",
        "Compare listed odds with an independent win-probability estimate.",
        "positioniq_pages/expected_value.py",
        "Open EV Calculator",
        ":material/trending_up:",
    )

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    tool_card(
        "🛡️",
        "Plan a hedge",
        "See how an opposing wager changes upside, downside, and risk.",
        "positioniq_pages/hedge.py",
        "Open Hedge Calculator",
        ":material/shield:",
    )

with row2_col2:
    tool_card(
        "💵",
        "Review a cashout offer",
        "Compare guaranteed cash with ticket value and remaining upside.",
        "positioniq_pages/cashout.py",
        "Open Cashout Analyzer",
        ":material/paid:",
    )

with row2_col3:
    tool_card(
        "🧩",
        "Build or monitor a parlay",
        "Analyze ticket structure, pricing, line movement, and hedging.",
        "positioniq_pages/parlay_lab.py",
        "Open Parlay Lab",
        ":material/account_tree:",
    )

st.divider()

info_col1, info_col2 = st.columns(2)

with info_col1:
    if experience_level == "Beginner":
        st.subheader("Three ideas to understand first")
        st.markdown(
            """
            1. **Odds are prices, not predictions.**
            2. **Profit and total return are different.**
            3. **A better long-term decision can still lose today.**
            """
        )
    else:
        st.subheader("Methodology at a glance")
        st.markdown(
            """
            - Decimal odds are the internal price format.
            - No-vig estimates use proportional normalization.
            - Cashout valuation uses remaining win probability.
            - Separate parlay events are assumed independent.
            - Exact SGP prices can retain embedded sportsbook margin.
            """
        )

with info_col2:
    st.subheader("Use the output responsibly")
    st.markdown(
        """
        - PositionIQ does not guarantee outcomes.
        - It does not create a model for every market.
        - It does not place bets or access sportsbook accounts.
        - It does not replace bankroll limits.
        """
    )

st.info(
    "Start with the tool matching your decision, then use the PositionIQ "
    "Takeaway and methodology sections to interpret the result."
)
