import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

st.header("Expected Value Calculator")

render_tool_intro(
    "Does the listed payout justify the probability assigned to this wager?",
    "The result is only as reliable as the probability entered. A positive "
    "result does not mean this specific wager will win.",
)


example_col1, example_col2, reset_col = st.columns(3)

with example_col1:
    if st.button("Load positive-EV example", key="ev_example_positive"):
        st.session_state["ev_format"] = "American"
        st.session_state["ev_american"] = 150
        st.session_state["ev_user_probability"] = 45.00
        st.session_state["ev_stake"] = 100.00
        st.rerun()

with example_col2:
    if st.button("Load break-even example", key="ev_example_even"):
        st.session_state["ev_format"] = "American"
        st.session_state["ev_american"] = -110
        st.session_state["ev_user_probability"] = 52.38
        st.session_state["ev_stake"] = 100.00
        st.rerun()

with reset_col:
    if st.button("Reset EV tool", key="reset_ev"):
        reset_keys(
            [
                "ev_format",
                "ev_american",
                "ev_decimal",
                "ev_fractional",
                "ev_implied_probability",
                "ev_user_probability",
                "ev_stake",
            ]
        )

st.info(
    "Expected value estimates the average profit or loss you would expect "
    "if the same wager could be repeated many times under the same odds "
    "and probability assumptions."
)

with st.expander("What is expected value?"):
    st.markdown(
        """
        A wager can lose today and still have positive expected value.
        It can also win today while being a poor long-term wager.

        Expected value compares:

        - The sportsbook's price
        - Your estimated probability of winning
        - The amount you plan to risk

        **Positive EV** means your probability estimate is high enough
        to justify the listed price.

        **Negative EV** means the listed payout is not large enough for
        the probability you assigned.

        Expected value depends completely on the quality of your
        probability estimate. PositionIQ does not generate that estimate
        for you in this version.
        """
    )

ev_format = st.selectbox(
    "Odds format",
    [
        "American",
        "Decimal",
        "Fractional",
        "Implied probability",
    ],
    key="ev_format",
)

try:
    input_col1, input_col2 = st.columns(2)

    with input_col1:
        if ev_format == "American":
            ev_odds_input = st.number_input(
                "Listed American odds",
                value=150,
                step=5,
                key="ev_american",
            )
        elif ev_format == "Decimal":
            ev_odds_input = st.number_input(
                "Listed decimal odds",
                min_value=1.01,
                value=2.50,
                step=0.01,
                format="%.2f",
                key="ev_decimal",
            )
        elif ev_format == "Fractional":
            ev_odds_input = st.text_input(
                "Listed fractional odds",
                value="3/2",
                key="ev_fractional",
            )
        else:
            ev_odds_input = st.number_input(
                "Listed implied probability (%)",
                min_value=0.01,
                max_value=99.99,
                value=40.00,
                step=0.01,
                format="%.2f",
                key="ev_implied_probability",
            )

    if experience_level == "Beginner":
        st.warning(
            "PositionIQ is not predicting the game here. The probability "
            "entered below must come from your own model, research, or a "
            "separate market-based estimate."
        )
    else:
        st.caption(
            "Probability input is exogenous to PositionIQ and determines "
            "the EV result."
        )

    with input_col2:
        estimated_probability = st.number_input(
            "Your estimated win probability (%)",
            min_value=0.01,
            max_value=99.99,
            value=45.00,
            step=0.25,
            format="%.2f",
            key="ev_user_probability",
            help=(
                "This should be your independent estimate of how often "
                "the wager would win—not the sportsbook's listed implied "
                "probability."
            ),
        )

    stake = st.number_input(
        "Stake amount ($)",
        min_value=0.01,
        value=100.00,
        step=10.00,
        format="%.2f",
        key="ev_stake",
    )

    ev_decimal_odds = convert_input_to_decimal(
        ev_format,
        ev_odds_input,
    )

    implied_probability = break_even_probability(
        ev_decimal_odds
    )

    edge_percent = probability_edge(
        ev_decimal_odds,
        estimated_probability,
    )

    ev_dollars = expected_value(
        stake,
        ev_decimal_odds,
        estimated_probability,
    )

    ev_percent = expected_value_percent(
        ev_decimal_odds,
        estimated_probability,
    )

    net_profit_if_win = calculate_profit(
        stake,
        ev_decimal_odds,
    )

    rating_icon, rating_label, rating_explanation = (
        get_ev_rating(ev_percent)
    )

    st.divider()
    st.subheader("Probability comparison")

    probability_col1, probability_col2, probability_col3 = st.columns(3)

    probability_col1.metric(
        "Break-even probability",
        f"{implied_probability:.2f}%",
    )

    probability_col2.metric(
        "Your estimated probability",
        f"{estimated_probability:.2f}%",
    )

    probability_col3.metric(
        "Estimated probability edge",
        f"{edge_percent:+.2f} pts",
        help=(
            "Your probability estimate minus the listed break-even "
            "probability."
        ),
    )

    st.subheader("Expected value results")

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric(
        "Expected value per wager",
        f"${ev_dollars:+,.2f}",
    )

    result_col2.metric(
        "Expected ROI",
        f"{ev_percent:+.2f}%",
    )

    result_col3.metric(
        "Profit if wager wins",
        f"${net_profit_if_win:,.2f}",
    )

    st.markdown("### PositionIQ EV Rating")

    with st.container(border=True):
        st.markdown(f"## {rating_icon} {rating_label}")
        st.write(rating_explanation)

    if ev_percent > 0:
        st.success(
            f"Based on your {estimated_probability:.2f}% probability "
            f"estimate, this wager has positive expected value of "
            f"${ev_dollars:,.2f} per ${stake:,.2f} wager."
        )
    elif abs(ev_percent) < 0.01:
        st.info(
            "Based on your estimate, this wager is approximately "
            "break-even before considering limits, errors, or changing "
            "market conditions."
        )
    else:
        st.warning(
            f"Based on your {estimated_probability:.2f}% probability "
            f"estimate, this wager has negative expected value of "
            f"${abs(ev_dollars):,.2f} per ${stake:,.2f} wager."
        )

    st.markdown("### Probability Sensitivity")

    sensitivity_probabilities = [
        max(0.01, estimated_probability - 2),
        estimated_probability,
        min(99.99, estimated_probability + 2),
    ]

    sensitivity_rows = []

    for sensitivity_probability in sensitivity_probabilities:
        sensitivity_rows.append(
            {
                "Estimated win probability": sensitivity_probability,
                "Expected value": expected_value(
                    stake,
                    ev_decimal_odds,
                    sensitivity_probability,
                ),
                "Expected ROI": expected_value_percent(
                    ev_decimal_odds,
                    sensitivity_probability,
                ),
            }
        )

    st.dataframe(
        sensitivity_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Estimated win probability": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Expected value": st.column_config.NumberColumn(
                format="$%.2f"
            ),
            "Expected ROI": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
        },
    )

    render_takeaway(
        (
            "The wager appears positive EV."
            if ev_percent > 0
            else "The wager appears negative EV."
        ),
        (
            f"At the entered {estimated_probability:.2f}% win estimate, "
            f"the average modeled result is ${ev_dollars:+,.2f} per "
            f"${stake:,.2f} wager."
        ),
        (
            "Small probability-estimation errors can erase a narrow edge. "
            "The sensitivity table shows how the result changes when the "
            "estimate moves by two percentage points."
        ),
    )

    with st.expander("How was this calculated?", expanded=advanced_mode):
        st.markdown(
            f"""
            **Listed decimal odds:** {ev_decimal_odds:.4f}

            **Break-even probability:** {implied_probability:.2f}%

            **Your estimated probability:** {estimated_probability:.2f}%

            **Probability edge:** {edge_percent:+.2f} percentage points

            **Expected value per wager:** ${ev_dollars:+,.2f}

            **Expected ROI:** {ev_percent:+.2f}%

            Expected value weighs the possible profit by your estimated
            chance of winning and subtracts the possible loss weighted by
            your estimated chance of losing.
            """
        )

    with st.expander("Important limitations", expanded=advanced_mode):
        st.markdown(
            """
            **Your probability estimate drives the result**

            Entering an overly optimistic probability will make almost
            any wager appear profitable.

            **Positive EV does not guarantee a win**

            Even a strong positive-EV wager can lose. EV describes an
            average across many comparable wagers.

            **Small edges are fragile**

            A small error in your probability estimate can erase a narrow
            edge.

            **Market odds can change**

            Expected value should be recalculated when the available price
            moves.

            **This version does not remove vig automatically**

            For a market-based probability estimate, use the no-vig
            calculator first and then compare that probability with the
            offered odds.
            """
        )

    st.caption(
        "For educational and analytical purposes. PositionIQ does not "
        "predict outcomes or guarantee profitability."
    )

except ValueError as error:
    st.error(str(error))
