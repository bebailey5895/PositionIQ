import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

st.markdown(
    """
    <div class="pi-hero">
        <div class="pi-kicker">Sports betting decision tools</div>
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

st.markdown(
    '<div class="pi-section-label">Choose your situation</div>',
    unsafe_allow_html=True,
)

row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">🔄</div>
            <h3>Understand the odds</h3>
            <p>Translate odds formats and see profit, total return, and
            break-even probability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: Odds Converter")

with row1_col2:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">⚖️</div>
            <h3>Estimate the market probability</h3>
            <p>Remove the sportsbook's estimated margin from a complete
            two-way or three-way market.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: No-Vig Calculator")

with row1_col3:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">📈</div>
            <h3>Evaluate a price</h3>
            <p>Compare the listed break-even probability with an
            independent probability estimate.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: EV Calculator")

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">🛡️</div>
            <h3>Plan a hedge</h3>
            <p>See how a second wager changes upside, downside, and the
            worst possible outcome.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: Hedge Calculator")

with row2_col2:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">💵</div>
            <h3>Review a cashout offer</h3>
            <p>Compare guaranteed cash with the estimated current value
            and remaining upside of the ticket.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: Cashout Analyzer")

with row2_col3:
    st.markdown(
        """
        <div class="pi-card">
            <div class="pi-icon">🧩</div>
            <h3>Build or monitor a parlay</h3>
            <p>Reconstruct the ticket by event, compare component prices,
            monitor line movement, and plan a final-event hedge.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use: Parlay Lab")

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
    st.subheader("What PositionIQ does not do")
    st.markdown(
        """
        - It does not guarantee outcomes.
        - It does not create a probability model for every market.
        - It does not place bets or access sportsbook accounts.
        - It does not replace bankroll limits or responsible gambling.
        """
    )

st.info(
    "Start with the tool matching your decision, then use the glossary "
    "and PositionIQ Takeaway boxes to interpret the result."
)
