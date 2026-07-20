import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

st.header("Two-Outcome Hedge Calculator")

render_tool_intro(
    "How would a second wager change my possible profit and loss?",
    "A hedge reduces risk by giving up some maximum upside. It does not "
    "create value automatically.",
)


example_col1, example_col2 = st.columns(2)

with example_col1:
    if st.button("Load equal-profit example", key="hedge_example"):
        st.session_state["hedge_format"] = "American"
        st.session_state["hedge_original_stake"] = 100.00
        st.session_state["hedge_original_american"] = 120
        st.session_state["hedge_opposing_american"] = -110
        st.session_state["hedge_strategy"] = (
            "Lock in the same profit either way"
        )
        st.rerun()

with example_col2:
    if st.button("Reset hedge tool", key="reset_hedge"):
        reset_keys(
            [
                "hedge_format",
                "hedge_original_stake",
                "hedge_original_american",
                "hedge_opposing_american",
                "hedge_original_decimal",
                "hedge_opposing_decimal",
                "hedge_original_fractional",
                "hedge_opposing_fractional",
                "hedge_original_probability",
                "hedge_opposing_probability",
                "hedge_strategy",
                "hedge_custom_amount",
            ]
        )

st.info(
    "Hedging means placing a second wager on the opposing outcome to "
    "reduce risk. It can lock in profit, recover your original stake, "
    "or reduce a potential loss—but it also lowers your maximum upside."
)

with st.expander("What is hedging, and why would I do it?"):
    st.markdown(
        """
        Hedging is similar to buying insurance on an existing wager.

        People commonly hedge to lock in profit, recover their original
        stake, reduce exposure, protect a parlay before its final leg, or
        avoid risking an amount they are no longer comfortable losing.

        Hedging is optional. Letting the original wager ride preserves
        the highest possible upside.
        """
    )

with st.expander("When should I use this calculator?"):
    st.markdown(
        """
        Appropriate examples:

        - A two-way moneyline
        - Team to qualify or advance
        - A spread or total with no push possibility
        - Hedging the final leg of a parlay with one opposing outcome

        Do not use this simple version when a draw, push, void, or third
        outcome can leave both wagers losing.
        """
    )

hedge_format = st.selectbox(
    "Odds format",
    [
        "American",
        "Decimal",
        "Fractional",
        "Implied probability",
    ],
    key="hedge_format",
)

try:
    original_stake = st.number_input(
        "Original stake ($)",
        min_value=0.01,
        value=100.00,
        step=10.00,
        format="%.2f",
        key="hedge_original_stake",
    )

    original_col, hedge_col = st.columns(2)

    if hedge_format == "American":
        with original_col:
            original_input = st.number_input(
                "Original wager odds",
                value=120,
                step=5,
                key="hedge_original_american",
            )

        with hedge_col:
            hedge_input = st.number_input(
                "Current opposing hedge odds",
                value=-110,
                step=5,
                key="hedge_opposing_american",
            )

    elif hedge_format == "Decimal":
        with original_col:
            original_input = st.number_input(
                "Original wager decimal odds",
                min_value=1.01,
                value=2.20,
                step=0.01,
                format="%.2f",
                key="hedge_original_decimal",
            )

        with hedge_col:
            hedge_input = st.number_input(
                "Current hedge decimal odds",
                min_value=1.01,
                value=1.91,
                step=0.01,
                format="%.2f",
                key="hedge_opposing_decimal",
            )

    elif hedge_format == "Fractional":
        with original_col:
            original_input = st.text_input(
                "Original wager fractional odds",
                value="6/5",
                key="hedge_original_fractional",
            )

        with hedge_col:
            hedge_input = st.text_input(
                "Current hedge fractional odds",
                value="10/11",
                key="hedge_opposing_fractional",
            )

    else:
        with original_col:
            original_input = st.number_input(
                "Original implied probability (%)",
                min_value=0.01,
                max_value=99.99,
                value=45.45,
                step=0.01,
                format="%.2f",
                key="hedge_original_probability",
            )

        with hedge_col:
            hedge_input = st.number_input(
                "Hedge implied probability (%)",
                min_value=0.01,
                max_value=99.99,
                value=52.38,
                step=0.01,
                format="%.2f",
                key="hedge_opposing_probability",
            )

    original_decimal = convert_input_to_decimal(
        hedge_format,
        original_input,
    )

    hedge_decimal = convert_input_to_decimal(
        hedge_format,
        hedge_input,
    )

    original_unhedged_profit = calculate_profit(
        original_stake,
        original_decimal,
    )

    original_total_return = calculate_total_return(
        original_stake,
        original_decimal,
    )

    st.divider()
    st.subheader("Before hedging")

    before_col1, before_col2, before_col3 = st.columns(3)

    before_col1.metric(
        "If original wager wins",
        f"${original_unhedged_profit:,.2f}",
    )

    before_col2.metric(
        "If original wager loses",
        f"-${original_stake:,.2f}",
    )

    before_col3.metric(
        "Potential total return",
        f"${original_total_return:,.2f}",
    )

    strategy = st.selectbox(
        "What is your goal?",
        [
            "Lock in the same profit either way",
            "Get my original stake back if the hedge wins",
            "Hedge most of the risk",
            "Hedge half of the risk",
            "Hedge a small portion",
            "Choose my own hedge amount",
        ],
        key="hedge_strategy",
    )

    equal_hedge = full_hedge_amount(
        original_stake,
        original_decimal,
        hedge_decimal,
    )

    if strategy == "Lock in the same profit either way":
        hedge_stake = equal_hedge
    elif strategy == "Get my original stake back if the hedge wins":
        hedge_stake = stake_protection_hedge_amount(
            original_stake,
            hedge_decimal,
        )
    elif strategy == "Hedge most of the risk":
        hedge_stake = equal_hedge * 0.75
    elif strategy == "Hedge half of the risk":
        hedge_stake = equal_hedge * 0.50
    elif strategy == "Hedge a small portion":
        hedge_stake = equal_hedge * 0.25
    else:
        hedge_stake = st.number_input(
            "Custom hedge amount ($)",
            min_value=0.00,
            value=50.00,
            step=10.00,
            format="%.2f",
            key="hedge_custom_amount",
        )

    profit_original, profit_hedge = hedge_outcome_profits(
        original_stake,
        original_decimal,
        hedge_stake,
        hedge_decimal,
    )

    guaranteed_result = min(
        profit_original,
        profit_hedge,
    )

    upside_given_up = (
        original_unhedged_profit - profit_original
    )

    st.divider()
    st.subheader("Recommended hedge")

    recommendation_col1, recommendation_col2, recommendation_col3 = (
        st.columns(3)
    )

    recommendation_col1.metric(
        "Recommended hedge amount",
        f"${hedge_stake:,.2f}",
    )

    recommendation_col2.metric(
        "Total amount risked",
        f"${original_stake + hedge_stake:,.2f}",
    )

    recommendation_col3.metric(
        "Original upside given up",
        f"${upside_given_up:,.2f}",
    )

    st.subheader("After hedging")

    outcome_a, outcome_b = st.columns(2)

    with outcome_a:
        st.markdown("### Original wager wins")
        st.metric(
            "Net profit",
            f"${profit_original:,.2f}",
        )

    with outcome_b:
        st.markdown("### Hedge wager wins")
        st.metric(
            "Net profit",
            f"${profit_hedge:,.2f}",
        )

    comparison_rows = [
        {
            "Outcome": "Original wager wins",
            "No hedge": original_unhedged_profit,
            "Selected hedge": profit_original,
        },
        {
            "Outcome": "Opposing outcome wins",
            "No hedge": -original_stake,
            "Selected hedge": profit_hedge,
        },
    ]

    st.markdown("### Before vs. After")
    st.dataframe(
        comparison_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No hedge": st.column_config.NumberColumn(
                format="$%.2f"
            ),
            "Selected hedge": st.column_config.NumberColumn(
                format="$%.2f"
            ),
        },
    )

    if guaranteed_result > 0:
        st.success(
            f"This setup guarantees at least "
            f"${guaranteed_result:,.2f} in net profit."
        )
    elif abs(guaranteed_result) < 0.005:
        st.info(
            "This setup approximately eliminates the worst-case loss."
        )
    else:
        st.warning(
            f"One outcome still produces a loss of "
            f"${abs(guaranteed_result):,.2f}."
        )

    render_takeaway(
        "The hedge exchanges upside for protection.",
        (
            f"The selected hedge gives up ${upside_given_up:,.2f} of "
            f"maximum upside. The worst resulting outcome is "
            f"${guaranteed_result:,.2f}."
        ),
        (
            "The calculation assumes exactly two mutually exclusive "
            "outcomes and that both wagers settle normally."
        ),
    )

    with st.expander("What does this hedge trade off?"):
        st.markdown(
            f"""
            - Equal-profit hedge amount: **${equal_hedge:,.2f}**
            - Selected hedge amount: **${hedge_stake:,.2f}**
            - Profit if original wins: **${profit_original:,.2f}**
            - Profit if hedge wins: **${profit_hedge:,.2f}**
            - Original upside given up:
              **${upside_given_up:,.2f}**

            Hedging changes the distribution of outcomes; it does not
            create value by itself.
            """
        )

    st.caption(
        "This calculator assumes exactly two mutually exclusive outcomes "
        "and does not account for pushes, voids, fees, taxes, partial "
        "settlements, or sportsbook limits."
    )

except ValueError as error:
    st.error(str(error))
