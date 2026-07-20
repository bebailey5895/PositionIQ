import streamlit as st

from positioniq_calculations import (
    american_to_decimal,
    calculate_profit,
    calculate_total_return,
    decimal_to_american,
    decimal_to_fractional,
    decimal_to_probability,
    expected_value,
    expected_value_percent,
    fractional_to_decimal,
    full_hedge_amount,
    hedge_outcome_profits,
    probability_edge,
    probability_to_decimal,
    remove_vig_three_way,
    remove_vig_two_way,
    stake_protection_hedge_amount,
)


st.set_page_config(
    page_title="PositionIQ",
    page_icon="📊",
    layout="centered",
)


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


st.title("PositionIQ")
st.caption("Understand every possible outcome.")

converter_tab, no_vig_tab, hedge_tab, ev_tab = st.tabs(
    [
        "Odds Converter",
        "No-Vig Calculator",
        "Hedge Calculator",
        "EV Calculator",
    ]
)


# =========================================================
# ODDS CONVERTER
# =========================================================

with converter_tab:
    st.header("Universal Odds Converter")

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


# =========================================================
# NO-VIG CALCULATOR
# =========================================================

with no_vig_tab:
    st.header("No-Vig Calculator")

    market_type = st.radio(
        "Market structure",
        [
            "Two-way market",
            "Three-way regulation market",
        ],
        horizontal=True,
    )

    no_vig_format = st.selectbox(
        "Input format",
        [
            "American",
            "Decimal",
            "Implied probability",
        ],
        key="no_vig_format",
    )

    try:
        if market_type == "Two-way market":
            st.caption(
                "Use for spreads, totals, props, or qualification markets "
                "where exactly one of two outcomes must occur."
            )

            side_a_name = "Outcome A"
            side_b_name = "Outcome B"

            with st.expander(
                "Customize outcome labels (optional)",
                expanded=False,
            ):
                label_col1, label_col2 = st.columns(2)

                with label_col1:
                    custom_side_a_name = st.text_input(
                        "Outcome A label",
                        value="",
                        placeholder="Example: Chiefs",
                        key="two_way_custom_name_a",
                    )

                with label_col2:
                    custom_side_b_name = st.text_input(
                        "Outcome B label",
                        value="",
                        placeholder="Example: Bills",
                        key="two_way_custom_name_b",
                    )

                if custom_side_a_name.strip():
                    side_a_name = custom_side_a_name.strip()

                if custom_side_b_name.strip():
                    side_b_name = custom_side_b_name.strip()

            input_col1, input_col2 = st.columns(2)

            if no_vig_format == "American":
                with input_col1:
                    side_a_input = st.number_input(
                        f"{side_a_name} American odds",
                        value=-120,
                        step=5,
                        key="two_way_a_american",
                    )
                with input_col2:
                    side_b_input = st.number_input(
                        f"{side_b_name} American odds",
                        value=105,
                        step=5,
                        key="two_way_b_american",
                    )
            elif no_vig_format == "Decimal":
                with input_col1:
                    side_a_input = st.number_input(
                        f"{side_a_name} decimal odds",
                        min_value=1.01,
                        value=1.83,
                        step=0.01,
                        format="%.2f",
                        key="two_way_a_decimal",
                    )
                with input_col2:
                    side_b_input = st.number_input(
                        f"{side_b_name} decimal odds",
                        min_value=1.01,
                        value=2.05,
                        step=0.01,
                        format="%.2f",
                        key="two_way_b_decimal",
                    )
            else:
                with input_col1:
                    side_a_input = st.number_input(
                        f"{side_a_name} implied probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=54.55,
                        step=0.01,
                        format="%.2f",
                        key="two_way_a_probability",
                    )
                with input_col2:
                    side_b_input = st.number_input(
                        f"{side_b_name} implied probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=48.78,
                        step=0.01,
                        format="%.2f",
                        key="two_way_b_probability",
                    )

            side_a_decimal = convert_input_to_decimal(
                no_vig_format,
                side_a_input,
            )
            side_b_decimal = convert_input_to_decimal(
                no_vig_format,
                side_b_input,
            )

            raw_a = decimal_to_probability(side_a_decimal)
            raw_b = decimal_to_probability(side_b_decimal)

            fair_a, fair_b, market_margin = remove_vig_two_way(
                side_a_decimal,
                side_b_decimal,
            )

            combined_probability = raw_a + raw_b

            st.divider()
            st.subheader("Market analysis")

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Combined probability",
                f"{combined_probability:.2f}%",
            )
            c2.metric(
                "Estimated overround",
                f"{market_margin:.2f}%",
            )
            c3.metric("No-vig total", "100.00%")

            display_market_context(
                market_margin,
                combined_probability,
            )

            st.divider()
            st.subheader("No-vig estimates")

            result_a, result_b = st.columns(2)

            with result_a:
                st.markdown(f"### {side_a_name}")
                st.metric("Listed probability", f"{raw_a:.2f}%")
                st.metric("No-vig probability", f"{fair_a:.2f}%")
                fair_decimal_a = probability_to_decimal(fair_a)
                st.metric(
                    "Fair American odds",
                    f"{decimal_to_american(fair_decimal_a):+.0f}",
                )
                st.metric(
                    "Fair decimal odds",
                    f"{fair_decimal_a:.4f}",
                )

            with result_b:
                st.markdown(f"### {side_b_name}")
                st.metric("Listed probability", f"{raw_b:.2f}%")
                st.metric("No-vig probability", f"{fair_b:.2f}%")
                fair_decimal_b = probability_to_decimal(fair_b)
                st.metric(
                    "Fair American odds",
                    f"{decimal_to_american(fair_decimal_b):+.0f}",
                )
                st.metric(
                    "Fair decimal odds",
                    f"{fair_decimal_b:.4f}",
                )

        else:
            st.caption(
                "Use for soccer regulation markets: home win, draw, and "
                "away win after 90 minutes plus stoppage time."
            )

            side_a_name = "Home"
            draw_name = "Draw"
            side_b_name = "Away"

            with st.expander(
                "Customize team names (optional)",
                expanded=False,
            ):
                team_col1, team_col2 = st.columns(2)

                with team_col1:
                    custom_home_name = st.text_input(
                        "Home team",
                        value="",
                        placeholder="Example: Argentina",
                        key="three_way_custom_home",
                    )

                with team_col2:
                    custom_away_name = st.text_input(
                        "Away team",
                        value="",
                        placeholder="Example: Brazil",
                        key="three_way_custom_away",
                    )

                if custom_home_name.strip():
                    side_a_name = custom_home_name.strip()

                if custom_away_name.strip():
                    side_b_name = custom_away_name.strip()

            input_a, input_draw, input_b = st.columns(3)

            if no_vig_format == "American":
                with input_a:
                    side_a_input = st.number_input(
                        f"{side_a_name} odds",
                        value=120,
                        step=5,
                        key="three_way_a_american",
                    )
                with input_draw:
                    draw_input = st.number_input(
                        f"{draw_name} odds",
                        value=240,
                        step=5,
                        key="three_way_draw_american",
                    )
                with input_b:
                    side_b_input = st.number_input(
                        f"{side_b_name} odds",
                        value=220,
                        step=5,
                        key="three_way_b_american",
                    )
            elif no_vig_format == "Decimal":
                with input_a:
                    side_a_input = st.number_input(
                        f"{side_a_name} decimal",
                        min_value=1.01,
                        value=2.20,
                        step=0.01,
                        format="%.2f",
                        key="three_way_a_decimal",
                    )
                with input_draw:
                    draw_input = st.number_input(
                        f"{draw_name} decimal",
                        min_value=1.01,
                        value=3.40,
                        step=0.01,
                        format="%.2f",
                        key="three_way_draw_decimal",
                    )
                with input_b:
                    side_b_input = st.number_input(
                        f"{side_b_name} decimal",
                        min_value=1.01,
                        value=3.20,
                        step=0.01,
                        format="%.2f",
                        key="three_way_b_decimal",
                    )
            else:
                with input_a:
                    side_a_input = st.number_input(
                        f"{side_a_name} probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=45.45,
                        step=0.01,
                        format="%.2f",
                        key="three_way_a_probability",
                    )
                with input_draw:
                    draw_input = st.number_input(
                        f"{draw_name} probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=29.41,
                        step=0.01,
                        format="%.2f",
                        key="three_way_draw_probability",
                    )
                with input_b:
                    side_b_input = st.number_input(
                        f"{side_b_name} probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=31.25,
                        step=0.01,
                        format="%.2f",
                        key="three_way_b_probability",
                    )

            side_a_decimal = convert_input_to_decimal(
                no_vig_format,
                side_a_input,
            )
            draw_decimal = convert_input_to_decimal(
                no_vig_format,
                draw_input,
            )
            side_b_decimal = convert_input_to_decimal(
                no_vig_format,
                side_b_input,
            )

            raw_a = decimal_to_probability(side_a_decimal)
            raw_draw = decimal_to_probability(draw_decimal)
            raw_b = decimal_to_probability(side_b_decimal)

            (
                fair_a,
                fair_draw,
                fair_b,
                market_margin,
            ) = remove_vig_three_way(
                side_a_decimal,
                draw_decimal,
                side_b_decimal,
            )

            combined_probability = raw_a + raw_draw + raw_b

            st.divider()
            st.subheader("Market analysis")

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Combined probability",
                f"{combined_probability:.2f}%",
            )
            c2.metric(
                "Estimated overround",
                f"{market_margin:.2f}%",
            )
            c3.metric("No-vig total", "100.00%")

            display_market_context(
                market_margin,
                combined_probability,
            )

            st.divider()
            st.subheader("Three-way no-vig estimates")

            result_a, result_draw, result_b = st.columns(3)

            results = [
                (result_a, side_a_name, raw_a, fair_a),
                (result_draw, draw_name, raw_draw, fair_draw),
                (result_b, side_b_name, raw_b, fair_b),
            ]

            for column, name, raw_probability, fair_probability in results:
                with column:
                    st.markdown(f"### {name}")
                    st.metric(
                        "Listed probability",
                        f"{raw_probability:.2f}%",
                    )
                    st.metric(
                        "No-vig probability",
                        f"{fair_probability:.2f}%",
                    )
                    fair_decimal = probability_to_decimal(
                        fair_probability
                    )
                    st.metric(
                        "Fair American odds",
                        f"{decimal_to_american(fair_decimal):+.0f}",
                    )
                    st.metric(
                        "Fair decimal odds",
                        f"{fair_decimal:.4f}",
                    )

        st.caption(
            "PositionIQ uses proportional normalization. Other no-vig "
            "methods may produce slightly different results."
        )

    except ValueError as error:
        st.error(str(error))


# =========================================================
# HEDGE CALCULATOR
# =========================================================

with hedge_tab:
    st.header("Two-Outcome Hedge Calculator")

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


# =========================================================
# EXPECTED VALUE CALCULATOR
# =========================================================

with ev_tab:
    st.header("Expected Value Calculator")

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

        implied_probability = decimal_to_probability(
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

        with st.expander("How was this calculated?"):
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

        with st.expander("Important limitations"):
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


st.divider()
st.caption(
    "PositionIQ v0.5 — Odds conversion, two-way and three-way no-vig "
    "analysis, hedge calculations, and expected value analysis."
)
