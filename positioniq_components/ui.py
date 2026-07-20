"""Reusable PositionIQ interface components."""

import streamlit as st

from positioniq_calculations import (
    american_to_decimal,
    decimal_to_american,
    decimal_to_probability,
    fractional_to_decimal,
    probability_to_decimal,
)


def get_experience_level() -> str:
    """Return the active explanation level."""
    return st.session_state.get("experience_level", "Beginner")


def is_advanced_mode() -> bool:
    """Return True when advanced explanations are selected."""
    return get_experience_level() == "Advanced"


def reset_keys(keys: list[str]) -> None:
    """Remove selected widget values from session state."""
    for key in keys:
        st.session_state.pop(key, None)
    st.rerun()


def render_tool_intro(
    question: str,
    beginner_note: str,
) -> None:
    """Display mode-aware tool guidance."""
    if get_experience_level() == "Beginner":
        with st.container(border=True):
            st.markdown("#### What this tool answers")
            st.write(question)
            st.caption(beginner_note)
    else:
        st.caption(f"Purpose: {question}")


def render_takeaway(
    headline: str,
    meaning: str,
    uncertainty: str,
) -> None:
    """Display a mode-aware result summary."""
    safe_meaning = meaning.replace("$", r"\$")
    safe_uncertainty = uncertainty.replace("$", r"\$")

    if get_experience_level() == "Beginner":
        st.markdown("### PositionIQ Takeaway")

        with st.container(border=True):
            st.markdown(f"#### {headline}")
            st.markdown(safe_meaning)
            st.caption(
                f"What remains uncertain: {safe_uncertainty}"
            )
    else:
        st.markdown("### Analysis Summary")

        with st.container(border=True):
            st.markdown(f"**{headline}**")
            st.markdown(safe_meaning)
            st.markdown(
                f"**Primary limitation:** {safe_uncertainty}"
            )


def render_analysis_quality(
    quality: str,
    reasons: list[str],
) -> None:
    """Display a mode-aware analysis-quality indicator."""
    icon_map = {
        "High": "🟢",
        "Medium": "🟡",
        "Limited": "🟠",
    }

    icon = icon_map.get(quality, "⚪")

    with st.container(border=True):
        if get_experience_level() == "Beginner":
            st.markdown(
                f"#### {icon} How reliable is this estimate? {quality}"
            )
            beginner_explanations = {
                "High": (
                    "The calculation uses relatively complete market data."
                ),
                "Medium": (
                    "The calculation mixes stronger market data with some "
                    "listed sportsbook prices or assumptions."
                ),
                "Limited": (
                    "Treat this mainly as a pricing reference rather than a "
                    "precise probability estimate."
                ),
            }
            st.write(beginner_explanations.get(quality, ""))
        else:
            st.markdown(
                f"#### {icon} Analysis quality: {quality}"
            )

        for reason in reasons:
            st.write(f"• {reason}")


def get_margin_rating(
    market_margin: float,
) -> tuple[str, str, str]:
    if market_margin < 0:
        return (
            "🟢",
            "Potential Arbitrage",
            "The combined implied probability is below 100%.",
        )

    if market_margin < 2:
        return (
            "🟢",
            "Very Low Margin",
            "These prices are highly competitive.",
        )

    if market_margin < 4:
        return (
            "🟢",
            "Competitive Pricing",
            "This market has a relatively low built-in margin.",
        )

    if market_margin < 6:
        return (
            "🟡",
            "Typical Pricing",
            "This is a common range for standard sportsbook markets.",
        )

    if market_margin < 8:
        return (
            "🟠",
            "Expensive Pricing",
            "The market margin is higher than many standard markets.",
        )

    return (
        "🔴",
        "Very Expensive Pricing",
        "This market contains a substantial built-in margin.",
    )


def get_ev_rating(
    ev_percent: float,
) -> tuple[str, str, str]:
    if ev_percent >= 10:
        return (
            "🟢",
            "Strong Positive EV",
            "Your estimate implies a substantial theoretical edge.",
        )

    if ev_percent >= 3:
        return (
            "🟢",
            "Positive EV",
            "Your estimate implies a potentially favorable wager.",
        )

    if ev_percent > 0:
        return (
            "🟡",
            "Small Positive EV",
            "The estimated edge is positive but relatively narrow.",
        )

    if abs(ev_percent) < 0.01:
        return (
            "⚪",
            "Approximately Break-Even",
            "Your estimate is close to the listed break-even probability.",
        )

    if ev_percent > -5:
        return (
            "🟠",
            "Negative EV",
            "Your estimate suggests the listed price is unfavorable.",
        )

    return (
        "🔴",
        "Strong Negative EV",
        "Your estimate implies a substantial theoretical disadvantage.",
    )


def get_cashout_rating(
    value_difference: float,
    fair_value: float,
) -> tuple[str, str, str]:
    difference_percent = (
        value_difference / fair_value * 100
        if fair_value > 0
        else 0
    )

    if difference_percent >= 3:
        return (
            "🟢",
            "Offer Above Estimated Fair Value",
            "The cashout offer is higher than the ticket's estimated fair value.",
        )

    if difference_percent >= -2:
        return (
            "⚪",
            "Offer Near Estimated Fair Value",
            "The cashout offer is reasonably close to the ticket's estimated fair value.",
        )

    if difference_percent >= -7:
        return (
            "🟡",
            "Moderate Cashout Discount",
            "The sportsbook is offering somewhat less than the ticket's estimated fair value.",
        )

    return (
        "🔴",
        "Large Cashout Discount",
        "The sportsbook is offering substantially less than the ticket's estimated fair value.",
    )


def convert_input_to_decimal(
    odds_format: str,
    value: float | str,
) -> float:
    if odds_format == "American":
        return american_to_decimal(float(value))

    if odds_format == "Decimal":
        return float(value)

    if odds_format == "Fractional":
        return fractional_to_decimal(str(value))

    return probability_to_decimal(float(value))


def display_market_context(
    market_margin: float,
    combined_probability: float,
) -> None:
    rating_icon, rating_label, rating_explanation = (
        get_margin_rating(market_margin)
    )

    st.markdown("### Market Rating")

    with st.container(border=True):
        st.caption("Pricing Score")
        st.markdown(f"## {rating_icon} {rating_label}")
        st.write(rating_explanation)

    if market_margin > 0:
        st.info(
            f"This market contains an estimated overround of "
            f"{market_margin:.2f}%."
        )
    elif abs(market_margin) < 0.0001:
        st.success(
            "This market contains approximately no estimated overround."
        )
    else:
        st.warning(
            f"This market contains a negative estimated overround of "
            f"{market_margin:.2f}%."
        )

    with st.expander("What does this mean?"):
        st.markdown(
            f"""
            - Combined implied probability: **{combined_probability:.2f}%**
            - Estimated overround: **{market_margin:.2f}%**
            - Pricing rating: **{rating_icon} {rating_label}**

            A complete set of mutually exclusive outcomes should total 100%.
            Any amount above 100% is estimated overround. PositionIQ removes
            it proportionally to estimate fair no-vig prices.
            """
        )
