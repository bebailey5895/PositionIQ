import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

st.header("Universal Odds Converter")

render_tool_intro(
    "What do these odds mean in other formats, and what would the wager pay?",
    "Use this first when American, decimal, fractional, or probability "
    "formats are unfamiliar.",
)


example_col1, example_col2, reset_col = st.columns(3)

with example_col1:
    if st.button("Load +150 example", key="converter_example_plus"):
        st.session_state["converter_format"] = "American"
        st.session_state["converter_american"] = 150
        st.session_state["converter_stake"] = 100.00
        st.rerun()

with example_col2:
    if st.button("Load -150 example", key="converter_example_minus"):
        st.session_state["converter_format"] = "American"
        st.session_state["converter_american"] = -150
        st.session_state["converter_stake"] = 100.00
        st.rerun()

with reset_col:
    if st.button("Reset converter", key="reset_converter"):
        reset_keys(
            [
                "converter_format",
                "converter_american",
                "converter_decimal",
                "converter_fractional",
                "converter_probability",
                "converter_stake",
            ]
        )

odds_format = st.selectbox(
    "Input format",
    [
        "American",
        "Decimal",
        "Fractional",
        "Implied probability",
    ],
    key="converter_format",
)

try:
    if odds_format == "American":
        entered_odds = st.number_input(
            "Enter American odds",
            value=120,
            step=5,
            key="converter_american",
        )
    elif odds_format == "Decimal":
        entered_odds = st.number_input(
            "Enter decimal odds",
            min_value=1.01,
            value=2.20,
            step=0.01,
            format="%.2f",
            key="converter_decimal",
        )
    elif odds_format == "Fractional":
        entered_odds = st.text_input(
            "Enter fractional odds",
            value="6/5",
            key="converter_fractional",
        )
    else:
        entered_odds = st.number_input(
            "Enter implied probability (%)",
            min_value=0.01,
            max_value=99.99,
            value=45.45,
            step=0.01,
            format="%.2f",
            key="converter_probability",
        )

    decimal_odds = convert_input_to_decimal(
        odds_format,
        entered_odds,
    )

    american_odds = decimal_to_american(decimal_odds)
    fractional_odds = decimal_to_fractional(decimal_odds)
    implied_probability = decimal_to_probability(decimal_odds)

    st.divider()
    st.subheader("Converted odds")

    col1, col2 = st.columns(2)
    col1.metric("American", f"{american_odds:+.0f}")
    col2.metric("Decimal", f"{decimal_odds:.4f}")

    col3, col4 = st.columns(2)
    col3.metric("Fractional", fractional_odds)
    col4.metric(
        "Implied probability",
        f"{implied_probability:.2f}%",
    )

    st.divider()
    st.subheader("Payout example")

    stake = st.number_input(
        "Stake amount ($)",
        min_value=0.00,
        value=100.00,
        step=10.00,
        format="%.2f",
        key="converter_stake",
    )

    col5, col6 = st.columns(2)
    col5.metric(
        "Net profit",
        f"${calculate_profit(stake, decimal_odds):,.2f}",
    )
    col6.metric(
        "Total return",
        f"${calculate_total_return(stake, decimal_odds):,.2f}",
    )


    if stake > 0:
        net_profit = calculate_profit(stake, decimal_odds)
        total_return = calculate_total_return(stake, decimal_odds)

        render_takeaway(
            "This is the price and payout in plain language.",
            (
                f"A ${stake:,.2f} wager would return ${total_return:,.2f} "
                f"in total if it wins: ${net_profit:,.2f} profit plus the "
                f"original ${stake:,.2f} stake."
            ),
            (
                "Odds describe price, not certainty. The wager can still "
                "win or lose regardless of the implied probability."
            ),
        )

except ValueError as error:
    st.error(str(error))

with st.expander(
    "Learn about odds, vig, overround, and no-vig markets"
):
    st.markdown(
        """
        **Positive American odds** show profit on a $100 stake.
        `+120` means $120 profit on $100.

        **Negative American odds** show the stake needed to make $100.
        `-120` means risking $120 to make $100.

        **Vig** is the sportsbook's pricing advantage.

        **Overround** is the amount by which all listed implied
        probabilities exceed 100%.

        **No-vig probabilities** proportionally remove the overround so
        the outcomes total 100%. They are market estimates, not
        predictions.
        """
    )
