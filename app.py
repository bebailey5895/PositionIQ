import streamlit as st

from positioniq_calculations import (
    american_to_decimal,
    calculate_profit,
    calculate_total_return,
    decimal_to_american,
    decimal_to_fractional,
    decimal_to_probability,
    fractional_to_decimal,
    full_hedge_amount,
    hedge_outcome_profits,
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

    st.markdown("#### PositionIQ Insight")

    if market_margin < 0:
        st.success(
            "These prices may represent an arbitrage-style opportunity. "
            "Confirm every possible outcome is covered and all prices remain "
            "available before acting."
        )
    elif market_margin < 2:
        st.success(
            "This market is priced very competitively. Small price "
            "differences can become meaningful across many wagers."
        )
    elif market_margin < 4:
        st.info(
            "This market has relatively competitive pricing. Comparing "
            "multiple sportsbooks may still uncover a better price."
        )
    elif market_margin < 6:
        st.info(
            "This is a common sportsbook pricing range. A standard "
            "-110/-110 market contains approximately 4.76% overround."
        )
    elif market_margin < 8:
        st.warning(
            "This market is more expensive than many standard markets. "
            "Consider comparing prices elsewhere."
        )
    else:
        st.error(
            "This is a high-margin market. Props, futures, and same-game "
            "parlays often contain larger pricing margins."
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

            **General guide**

            - Under 2%: Very low
            - 2% to 4%: Competitive
            - 4% to 6%: Typical
            - 6% to 8%: Expensive
            - Above 8%: Very expensive
            """
        )

    with st.expander(
        "Useful details bettors often overlook",
        expanded=False,
    ):
        st.markdown(
            """
            **Overround is not actual sportsbook hold.** Actual hold depends
            on how wagers are distributed and settled.

            **No-vig odds are not predictions.** They estimate market prices
            after removing the listed margin.

            **Small differences matter.** Moving from -115 to -110 or +120
            to +125 can materially affect long-run results.

            **Market definitions matter.** A soccer three-way market covers
            home win, draw, and away win in regulation. A two-way
            qualification market covers which team advances, including extra
            time and penalties according to the sportsbook's rules.
            """
        )


st.title("PositionIQ")
st.caption("Understand every possible outcome.")

converter_tab, no_vig_tab, hedge_tab = st.tabs(
    [
        "Odds Converter",
        "No-Vig Calculator",
        "Hedge Calculator",
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
                (
                    result_a,
                    side_a_name,
                    raw_a,
                    fair_a,
                ),
                (
                    result_draw,
                    draw_name,
                    raw_draw,
                    fair_draw,
                ),
                (
                    result_b,
                    side_b_name,
                    raw_b,
                    fair_b,
                ),
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

            Suppose you placed a $100 wager on Team A at +500. That wager
            could return $600, but Team B later becomes available at a price
            that lets you protect part of your position.

            You could place a second wager on Team B. This lowers what you
            would win if Team A succeeds, but it gives you money back if
            Team B wins.

            People commonly hedge to:

            - Lock in guaranteed profit
            - Recover their original stake
            - Reduce exposure on a large wager
            - Protect a parlay before the final leg
            - Avoid risking an amount they are no longer comfortable losing

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
            help=(
                "This is how much less you would profit if the original "
                "wager wins after placing the hedge."
            ),
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

        st.subheader("What this hedge does")

        if strategy == "Lock in the same profit either way":
            st.success(
                "This strategy gives you approximately the same net result "
                "regardless of which wager wins."
            )

        elif strategy == "Get my original stake back if the hedge wins":
            st.info(
                "This strategy aims to recover your original stake if the "
                "hedge wins while preserving more upside on the original "
                "wager."
            )

        elif strategy == "Hedge most of the risk":
            st.info(
                "This substantially reduces your downside while preserving "
                "more profit if the original wager wins."
            )

        elif strategy == "Hedge half of the risk":
            st.info(
                "This balances protection and upside. It reduces risk "
                "without fully equalizing the two outcomes."
            )

        elif strategy == "Hedge a small portion":
            st.info(
                "This provides limited protection while keeping most of "
                "the original wager's upside."
            )

        else:
            st.info(
                "This custom amount lets you choose your own balance "
                "between protection and potential profit."
            )

        if guaranteed_result > 0:
            st.success(
                f"You are exchanging some upside for a guaranteed minimum "
                f"net profit of ${guaranteed_result:,.2f}."
            )

        elif abs(guaranteed_result) < 0.005:
            st.info(
                "This setup approximately eliminates your worst-case loss "
                "but does not guarantee additional profit."
            )

        else:
            st.warning(
                f"This hedge reduces risk, but one outcome still produces "
                f"a loss of ${abs(guaranteed_result):,.2f}."
            )

        with st.expander("What does this hedge trade off?"):
            st.markdown(
                f"""
                - Equal-profit hedge amount: **${equal_hedge:,.2f}**
                - Selected hedge amount: **${hedge_stake:,.2f}**
                - Profit if original wins: **${profit_original:,.2f}**
                - Profit if hedge wins: **${profit_hedge:,.2f}**
                - Original-wager upside given up:
                  **${upside_given_up:,.2f}**

                A larger hedge improves the hedge-side result but reduces
                the original wager's upside. Hedging changes the distribution
                of outcomes; it does not create value by itself.
                """
            )

        with st.expander("Common situations where people hedge"):
            st.markdown(
                """
                **Final leg of a parlay**

                Earlier legs have won, and the remaining leg determines
                whether the entire parlay pays.

                **Futures wager**

                A team reaches a championship or late tournament stage after
                being backed at long odds.

                **Live game movement**

                The original wager has improved significantly, and the
                opposing side is now available at a price that allows some
                risk protection.

                **The risk became uncomfortable**

                The possible loss or payout is larger than the bettor is
                comfortable leaving exposed.

                **Important:** Hedging is not automatically the best
                mathematical decision. It is primarily a risk-management
                choice.
                """
            )

        st.caption(
            "This calculator assumes exactly two mutually exclusive outcomes "
            "and does not account for pushes, voids, fees, taxes, partial "
            "settlements, or sportsbook limits."
        )

    except ValueError as error:
        st.error(str(error))


st.divider()
st.caption(
    "PositionIQ v0.4 — Odds conversion, two-way and three-way no-vig "
    "analysis, and two-outcome hedge calculations."
)
