import streamlit as st

from positioniq_calculations import (
    american_to_decimal,
    break_even_probability,
    calculate_profit,
    calculate_total_return,
    cashout_break_even_probability,
    cashout_offer_percentage,
    cashout_value_difference,
    combine_decimal_odds,
    combine_independent_probabilities,
    decimal_to_american,
    decimal_to_fractional,
    decimal_to_probability,
    expected_value,
    expected_value_percent,
    fair_cashout_value,
    fair_decimal_odds_from_probability,
    fractional_to_decimal,
    full_hedge_amount,
    hedge_outcome_profits,
    probability_edge,
    parlay_final_leg_equal_profit_hedge,
    parlay_final_leg_outcomes,
    probability_to_decimal,
    remove_vig_three_way,
    remove_vig_two_way,
    relative_price_difference_percent,
    stake_protection_hedge_amount,
)


st.set_page_config(
    page_title="PositionIQ",
    page_icon="📊",
    layout="centered",
)



def render_tool_intro(
    question: str,
    beginner_note: str,
) -> None:
    """Display a consistent beginner-friendly introduction."""
    with st.container(border=True):
        st.markdown("#### What this tool answers")
        st.write(question)
        st.caption(beginner_note)


def render_takeaway(
    headline: str,
    meaning: str,
    uncertainty: str,
) -> None:
    """Display a consistent plain-language result summary."""
    st.markdown("### PositionIQ Takeaway")

    with st.container(border=True):
        st.markdown(f"#### {headline}")
        st.write(meaning)
        st.caption(f"What remains uncertain: {uncertainty}")


def render_analysis_quality(
    quality: str,
    reasons: list[str],
) -> None:
    """Display an analysis-quality indicator."""
    icon_map = {
        "High": "🟢",
        "Medium": "🟡",
        "Limited": "🟠",
    }

    icon = icon_map.get(quality, "⚪")

    with st.container(border=True):
        st.markdown(f"#### {icon} Analysis quality: {quality}")

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


st.title("PositionIQ")
st.caption("Understand every possible outcome.")


with st.sidebar:
    st.header("PositionIQ Guide")

    experience_level = st.radio(
        "Explanation level",
        [
            "Beginner",
            "Advanced",
        ],
        key="global_explanation_level",
        help=(
            "Beginner mode emphasizes plain-language explanations. "
            "Advanced mode keeps the same results while surfacing more "
            "technical terminology."
        ),
    )

    st.divider()

    with st.expander("Sports betting glossary"):
        st.markdown(
            """
            **American odds**  
            Positive odds show profit on a $100 stake. Negative odds show
            how much must be risked to make $100.

            **Decimal odds**  
            Total return per $1 wagered, including the original stake.

            **Implied probability**  
            The break-even win rate represented by listed odds.

            **Break-even probability**  
            How often a wager must win to avoid losing money over time.

            **Vig**  
            The sportsbook's built-in pricing advantage.

            **Overround**  
            The amount by which all listed implied probabilities exceed 100%.

            **No-vig probability**  
            A market probability estimate after proportionally removing
            overround.

            **Expected value (EV)**  
            Estimated average profit or loss over many comparable wagers.

            **Expected ROI**  
            Expected value expressed as a percentage of the stake.

            **Hedge**  
            A second wager that changes the possible profit and loss across
            outcomes.

            **Cashout**  
            A sportsbook offer to settle an open ticket early.

            **Parlay**  
            A ticket that requires every included selection to win.

            **Same-game parlay**  
            Multiple selections from the same event, which may be correlated.

            **Correlation**  
            When one selection changes the likelihood of another selection.

            **Net profit**  
            Money won after subtracting the stake.

            **Total return**  
            Net profit plus the returned original stake.
            """
        )

    st.caption(
        "PositionIQ explains prices and trade-offs. It does not guarantee "
        "outcomes or profitability."
    )


converter_tab, no_vig_tab, hedge_tab, ev_tab, cashout_tab, parlay_tab = st.tabs(
    [
        "Odds Converter",
        "No-Vig Calculator",
        "Hedge Calculator",
        "EV Calculator",
        "Cashout Analyzer",
        "Parlay Lab",
    ]
)


# =========================================================
# ODDS CONVERTER
# =========================================================

with converter_tab:
    st.header("Universal Odds Converter")

    render_tool_intro(
        "What do these odds mean in other formats, and what would the wager pay?",
        "Use this first when American, decimal, fractional, or probability "
        "formats are unfamiliar.",
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


# =========================================================
# NO-VIG CALCULATOR
# =========================================================

with no_vig_tab:
    st.header("No-Vig Calculator")

    render_tool_intro(
        "What probability does the market suggest after removing the "
        "sportsbook's estimated pricing margin?",
        "The listed probabilities usually total more than 100%. PositionIQ "
        "scales them back to a 100% market.",
    )

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

        render_takeaway(
            "The market prices include a sportsbook margin.",
            (
                f"The listed outcomes total {combined_probability:.2f}%. "
                f"PositionIQ removes the estimated {market_margin:.2f}% "
                f"overround so the no-vig probabilities total 100%."
            ),
            (
                "No-vig probabilities reflect market pricing, not a guarantee "
                "or an independent prediction."
            ),
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

    render_tool_intro(
        "How would a second wager change my possible profit and loss?",
        "A hedge reduces risk by giving up some maximum upside. It does not "
        "create value automatically.",
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


# =========================================================
# EXPECTED VALUE CALCULATOR
# =========================================================

with ev_tab:
    st.header("Expected Value Calculator")

    render_tool_intro(
        "Does the listed payout justify the probability assigned to this wager?",
        "The result is only as reliable as the probability entered. A positive "
        "result does not mean this specific wager will win.",
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



# =========================================================
# CASHOUT ANALYZER
# =========================================================

with cashout_tab:
    st.header("Cashout Analyzer")

    render_tool_intro(
        "Is the sportsbook's cashout offer above or below the ticket's "
        "estimated current value?",
        "This compares expected value and certainty. It does not make the "
        "risk decision for the user.",
    )

    st.info(
        "A cashout offer should be compared with the ticket's estimated "
        "current value—not only with the original stake or potential profit."
    )

    with st.expander("How the Cashout Analyzer works"):
        st.markdown(
            """
            An unsettled ticket has an estimated current value:

            **Estimated fair ticket value = current win probability × total payout**

            PositionIQ compares that value with the sportsbook's cashout
            offer.

            - An offer below fair value includes a cashout discount.
            - An offer near fair value is relatively efficient.
            - An offer above fair value may be favorable to accept.

            This is still a risk decision. Continuing the wager preserves
            upside but can result in losing the entire current cashout value.
            """
        )

    cashout_odds_format = st.selectbox(
        "Original odds format",
        [
            "American",
            "Decimal",
            "Fractional",
            "Implied probability",
        ],
        key="cashout_original_format",
    )

    try:
        cashout_input_col1, cashout_input_col2 = st.columns(2)

        with cashout_input_col1:
            original_cashout_stake = st.number_input(
                "Original stake ($)",
                min_value=0.01,
                value=100.00,
                step=10.00,
                format="%.2f",
                key="cashout_original_stake",
            )

        with cashout_input_col2:
            cashout_offer = st.number_input(
                "Current cashout offer ($)",
                min_value=0.00,
                value=180.00,
                step=10.00,
                format="%.2f",
                key="cashout_offer",
            )

        if cashout_odds_format == "American":
            original_cashout_odds_input = st.number_input(
                "Original American odds",
                value=200,
                step=5,
                key="cashout_original_american",
            )
        elif cashout_odds_format == "Decimal":
            original_cashout_odds_input = st.number_input(
                "Original decimal odds",
                min_value=1.01,
                value=3.00,
                step=0.01,
                format="%.2f",
                key="cashout_original_decimal",
            )
        elif cashout_odds_format == "Fractional":
            original_cashout_odds_input = st.text_input(
                "Original fractional odds",
                value="2/1",
                key="cashout_original_fractional",
            )
        else:
            original_cashout_odds_input = st.number_input(
                "Original implied probability (%)",
                min_value=0.01,
                max_value=99.99,
                value=33.33,
                step=0.01,
                format="%.2f",
                key="cashout_original_probability",
            )

        original_cashout_decimal = convert_input_to_decimal(
            cashout_odds_format,
            original_cashout_odds_input,
        )

        total_payout = calculate_total_return(
            original_cashout_stake,
            original_cashout_decimal,
        )

        probability_method = st.radio(
            "How will you estimate the wager's current win probability?",
            [
                "Enter my own probability",
                "Use current two-way market odds",
            ],
            key="cashout_probability_method",
        )

        if probability_method == "Enter my own probability":
            current_win_probability = st.number_input(
                "Estimated current win probability (%)",
                min_value=0.01,
                max_value=99.99,
                value=65.00,
                step=0.25,
                format="%.2f",
                key="cashout_manual_probability",
                help=(
                    "Use your best current estimate of how often the ticket "
                    "would win from this point forward."
                ),
            )

            probability_source_note = (
                "The fair-value estimate uses your manually entered "
                "probability."
            )

        else:
            st.caption(
                "Enter prices for the ticket outcome and its exact opposite. "
                "PositionIQ removes the two-way market overround."
            )

            live_market_format = st.selectbox(
                "Current market odds format",
                [
                    "American",
                    "Decimal",
                    "Implied probability",
                ],
                key="cashout_live_market_format",
            )

            live_col1, live_col2 = st.columns(2)

            if live_market_format == "American":
                with live_col1:
                    ticket_outcome_input = st.number_input(
                        "Ticket outcome current odds",
                        value=-180,
                        step=5,
                        key="cashout_ticket_live_american",
                    )
                with live_col2:
                    opposite_outcome_input = st.number_input(
                        "Opposite outcome current odds",
                        value=155,
                        step=5,
                        key="cashout_opposite_live_american",
                    )
            elif live_market_format == "Decimal":
                with live_col1:
                    ticket_outcome_input = st.number_input(
                        "Ticket outcome current decimal odds",
                        min_value=1.01,
                        value=1.56,
                        step=0.01,
                        format="%.2f",
                        key="cashout_ticket_live_decimal",
                    )
                with live_col2:
                    opposite_outcome_input = st.number_input(
                        "Opposite outcome current decimal odds",
                        min_value=1.01,
                        value=2.55,
                        step=0.01,
                        format="%.2f",
                        key="cashout_opposite_live_decimal",
                    )
            else:
                with live_col1:
                    ticket_outcome_input = st.number_input(
                        "Ticket outcome listed probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=64.29,
                        step=0.01,
                        format="%.2f",
                        key="cashout_ticket_live_probability",
                    )
                with live_col2:
                    opposite_outcome_input = st.number_input(
                        "Opposite outcome listed probability (%)",
                        min_value=0.01,
                        max_value=99.99,
                        value=39.22,
                        step=0.01,
                        format="%.2f",
                        key="cashout_opposite_live_probability",
                    )

            ticket_live_decimal = convert_input_to_decimal(
                live_market_format,
                ticket_outcome_input,
            )
            opposite_live_decimal = convert_input_to_decimal(
                live_market_format,
                opposite_outcome_input,
            )

            (
                current_win_probability,
                opposite_fair_probability,
                current_market_overround,
            ) = remove_vig_two_way(
                ticket_live_decimal,
                opposite_live_decimal,
            )

            probability_source_note = (
                f"The probability estimate uses a two-way no-vig market. "
                f"Estimated current market overround: "
                f"{current_market_overround:.2f}%."
            )

        estimated_fair_value = fair_cashout_value(
            total_payout,
            current_win_probability,
        )


        if cashout_offer > total_payout:
            st.warning(
                "The cashout offer is greater than the ticket's maximum "
                "payout. Confirm that total payout includes the original "
                "stake and that the cashout amount was entered correctly."
            )

        if total_payout < original_cashout_stake:
            st.warning(
                "The total payout is below the original stake. Confirm that "
                "you entered total return rather than net profit."
            )

        break_even_cashout_probability = cashout_break_even_probability(
            cashout_offer,
            total_payout,
        )

        value_difference = cashout_value_difference(
            cashout_offer,
            estimated_fair_value,
        )

        offer_percentage = cashout_offer_percentage(
            cashout_offer,
            estimated_fair_value,
        )

        potential_profit = calculate_profit(
            original_cashout_stake,
            original_cashout_decimal,
        )

        additional_upside = total_payout - cashout_offer
        downside_from_declining = cashout_offer

        (
            cashout_icon,
            cashout_label,
            cashout_explanation,
        ) = get_cashout_rating(
            value_difference,
            estimated_fair_value,
        )

        st.divider()
        st.subheader("Ticket overview")

        overview_col1, overview_col2, overview_col3 = st.columns(3)

        overview_col1.metric(
            "Original stake",
            f"${original_cashout_stake:,.2f}",
        )
        overview_col2.metric(
            "Potential net profit",
            f"${potential_profit:,.2f}",
        )
        overview_col3.metric(
            "Total payout if it wins",
            f"${total_payout:,.2f}",
        )

        st.subheader("Cashout valuation")

        value_col1, value_col2, value_col3 = st.columns(3)

        value_col1.metric(
            "Estimated fair ticket value",
            f"${estimated_fair_value:,.2f}",
        )

        value_col2.metric(
            "Sportsbook cashout offer",
            f"${cashout_offer:,.2f}",
        )

        value_col3.metric(
            "Offer vs. fair value",
            f"${value_difference:+,.2f}",
        )

        comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

        comparison_col1.metric(
            "Current win probability",
            f"{current_win_probability:.2f}%",
        )

        comparison_col2.metric(
            "Offer as % of fair value",
            f"{offer_percentage:.2f}%",
        )

        comparison_col3.metric(
            "Cashout break-even probability",
            f"{break_even_cashout_probability:.2f}%",
            help=(
                "If your current win estimate is above this threshold, "
                "continuing has the higher expected value. If it is below "
                "this threshold, the cashout offer has the higher expected "
                "value."
            ),
        )

        st.markdown("### PositionIQ Cashout Rating")

        with st.container(border=True):
            st.markdown(f"## {cashout_icon} {cashout_label}")
            st.write(cashout_explanation)

        if value_difference >= 0:
            st.success(
                f"The offer is ${value_difference:,.2f} above the ticket's "
                f"estimated fair value under the selected probability "
                f"assumption."
            )
        else:
            st.warning(
                f"The offer is ${abs(value_difference):,.2f} below the "
                f"ticket's estimated fair value under the selected "
                f"probability assumption."
            )

        st.subheader("Decision trade-off")

        decision_col1, decision_col2 = st.columns(2)

        with decision_col1:
            st.markdown("#### Accept cashout")
            st.metric(
                "Guaranteed amount received",
                f"${cashout_offer:,.2f}",
            )
            st.caption(
                "Accepting removes all remaining outcome risk for this ticket."
            )

        with decision_col2:
            st.markdown("#### Continue wager")
            st.metric(
                "Additional upside over cashout",
                f"${additional_upside:,.2f}",
            )
            st.metric(
                "Current value at risk",
                f"${downside_from_declining:,.2f}",
            )

        if current_win_probability > break_even_cashout_probability:
            st.info(
                "Your selected probability is above the cashout break-even "
                "threshold, so continuing has the higher estimated value. "
                "That does not mean it is guaranteed to win."
            )
        elif current_win_probability < break_even_cashout_probability:
            st.info(
                "Your selected probability is below the cashout break-even "
                "threshold, so accepting the offer has the higher estimated "
                "value under this assumption."
            )
        else:
            st.info(
                "Your selected probability is approximately equal to the "
                "cashout break-even threshold."
            )

        render_takeaway(
            (
                "The offer is above estimated value."
                if value_difference >= 0
                else "The offer is below estimated value."
            ),
            (
                f"The offer is ${abs(value_difference):,.2f} "
                f"{'above' if value_difference >= 0 else 'below'} the "
                f"estimated ticket value. Accepting guarantees "
                f"${cashout_offer:,.2f}; declining keeps "
                f"${additional_upside:,.2f} of additional possible upside."
            ),
            (
                "The result depends on the current probability estimate and "
                "does not account for personal risk tolerance."
            ),
        )

        with st.expander("How was this calculated?"):
            st.markdown(
                f"""
                **Total payout if the ticket wins:** ${total_payout:,.2f}

                **Estimated current win probability:**
                {current_win_probability:.2f}%

                **Estimated fair ticket value:**
                ${estimated_fair_value:,.2f}

                **Cashout offer:** ${cashout_offer:,.2f}

                **Offer minus fair value:** ${value_difference:+,.2f}

                **Cashout break-even probability:**
                {break_even_cashout_probability:.2f}%

                {probability_source_note}
                """
            )

        with st.expander("Important limitations"):
            st.markdown(
                """
                - A fair cashout estimate requires a credible current win
                  probability.
                - Live markets can move quickly.
                - The two-way market method is inappropriate when a draw,
                  push, void, or third outcome can cause both positions to
                  lose.
                - Sportsbooks may account for limits, suspensions, settlement
                  rules, and operational risk differently.
                - A discounted cashout can still be reasonable for someone
                  who values certainty or needs to reduce exposure.
                - PositionIQ compares expected values; it does not tell users
                  what level of risk they must accept.
                """
            )

        st.caption(
            "For educational and analytical purposes. Cashout values are "
            "estimates and depend on the selected probability assumption."
        )

    except ValueError as error:
        st.error(str(error))



# =========================================================
# PARLAY LAB
# =========================================================

with parlay_tab:
    st.header("Parlay Lab")

    render_tool_intro(
        "How is this parlay structured, how does its offered price compare "
        "with its components, and what is the ticket worth while active?",
        "Build the ticket by event so same-game groups are not treated as "
        "independent selections.",
    )

    st.info(
        "Rebuild a parlay by event so PositionIQ can separate standalone "
        "selections from same-game groups, compare the offered ticket price "
        "with its component prices, and evaluate an active ticket."
    )

    builder_tab, live_tab, final_leg_tab = st.tabs(
        [
            "Ticket Builder",
            "Live Ticket & Cashout",
            "Final-Leg Hedge",
        ]
    )

    # -----------------------------------------------------
    # SHARED TICKET BUILDER
    # -----------------------------------------------------

    with builder_tab:
        st.subheader("Build the Exact Ticket")

        st.caption(
            "Selections from the same event are grouped together. "
            "A same-game group must use the sportsbook's exact combined "
            "price for that group; its selections are not multiplied as "
            "though they were independent."
        )

        try:
            ticket_col1, ticket_col2 = st.columns(2)

            with ticket_col1:
                parlay_stake = st.number_input(
                    "Parlay stake ($)",
                    min_value=0.01,
                    value=25.00,
                    step=5.00,
                    format="%.2f",
                    key="v08_parlay_stake",
                )

            with ticket_col2:
                event_count = st.number_input(
                    "Number of events in the parlay",
                    min_value=1,
                    max_value=8,
                    value=3,
                    step=1,
                    key="v08_event_count",
                )

            offered_format = st.selectbox(
                "Sportsbook's offered full-ticket odds format",
                [
                    "American",
                    "Decimal",
                    "Fractional",
                    "Implied probability",
                ],
                key="v08_offered_format",
            )

            if offered_format == "American":
                offered_ticket_input = st.number_input(
                    "Offered full-ticket American odds",
                    value=700,
                    step=10,
                    key="v08_offered_american",
                )
            elif offered_format == "Decimal":
                offered_ticket_input = st.number_input(
                    "Offered full-ticket decimal odds",
                    min_value=1.01,
                    value=8.00,
                    step=0.05,
                    format="%.2f",
                    key="v08_offered_decimal",
                )
            elif offered_format == "Fractional":
                offered_ticket_input = st.text_input(
                    "Offered full-ticket fractional odds",
                    value="7/1",
                    key="v08_offered_fractional",
                )
            else:
                offered_ticket_input = st.number_input(
                    "Offered full-ticket implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=12.50,
                    step=0.01,
                    format="%.2f",
                    key="v08_offered_probability",
                )

            offered_ticket_decimal = convert_input_to_decimal(
                offered_format,
                offered_ticket_input,
            )

            event_rows = []
            event_group_decimals = []
            event_group_probabilities = []
            total_selections = 0
            sgp_group_count = 0
            standalone_count = 0
            fair_probability_count = 0

            st.divider()
            st.markdown("### Event Groups")

            for event_index in range(int(event_count)):
                with st.expander(
                    f"Event {event_index + 1}",
                    expanded=(event_index == 0),
                ):
                    event_name = st.text_input(
                        "Event name",
                        value="",
                        placeholder="Example: Chiefs vs Bills",
                        key=f"v08_event_name_{event_index}",
                    ).strip() or f"Event {event_index + 1}"

                    group_type = st.radio(
                        "Group type",
                        [
                            "Standalone selection",
                            "Same-game group",
                        ],
                        horizontal=True,
                        key=f"v08_group_type_{event_index}",
                    )

                    if group_type == "Standalone selection":
                        standalone_count += 1
                        selection_count = 1
                    else:
                        sgp_group_count += 1
                        selection_count = st.number_input(
                            "Number of selections from this event",
                            min_value=2,
                            max_value=8,
                            value=2,
                            step=1,
                            key=f"v08_selection_count_{event_index}",
                        )

                    selection_labels = []

                    for selection_index in range(int(selection_count)):
                        label = st.text_input(
                            f"Selection {selection_index + 1}",
                            value="",
                            placeholder=(
                                "Example: Chiefs moneyline"
                                if selection_index == 0
                                else "Example: Over 47.5"
                            ),
                            key=(
                                f"v08_selection_{event_index}_"
                                f"{selection_index}"
                            ),
                        ).strip()

                        selection_labels.append(
                            label or f"Selection {selection_index + 1}"
                        )

                    total_selections += int(selection_count)

                    if group_type == "Standalone selection":
                        pricing_method = st.selectbox(
                            "How should this standalone selection be valued?",
                            [
                                "Complete two-way market (remove vig)",
                                "Complete three-way market (remove vig)",
                                "Selected price only",
                            ],
                            key=f"v08_pricing_method_{event_index}",
                        )
                    else:
                        pricing_method = "Exact same-game group price"

                    odds_format = st.selectbox(
                        "Event-group odds format",
                        [
                            "American",
                            "Decimal",
                            "Implied probability",
                        ],
                        key=f"v08_group_format_{event_index}",
                    )

                    if pricing_method == "Complete two-way market (remove vig)":
                        st.caption(
                            "Enter the selected outcome and its exact opposite."
                        )

                        price_col1, price_col2 = st.columns(2)

                        if odds_format == "American":
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected outcome odds",
                                    value=-120,
                                    step=5,
                                    key=f"v08_selected_2way_a_{event_index}",
                                )
                            with price_col2:
                                opposite_price = st.number_input(
                                    "Opposite outcome odds",
                                    value=105,
                                    step=5,
                                    key=f"v08_selected_2way_b_{event_index}",
                                )
                        elif odds_format == "Decimal":
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected outcome decimal odds",
                                    min_value=1.01,
                                    value=1.83,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_2way_da_{event_index}",
                                )
                            with price_col2:
                                opposite_price = st.number_input(
                                    "Opposite outcome decimal odds",
                                    min_value=1.01,
                                    value=2.05,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_2way_db_{event_index}",
                                )
                        else:
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=54.55,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_2way_pa_{event_index}",
                                )
                            with price_col2:
                                opposite_price = st.number_input(
                                    "Opposite listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=48.78,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_2way_pb_{event_index}",
                                )

                        selected_decimal = convert_input_to_decimal(
                            odds_format,
                            selected_price,
                        )
                        opposite_decimal = convert_input_to_decimal(
                            odds_format,
                            opposite_price,
                        )

                        (
                            group_probability,
                            _,
                            group_overround,
                        ) = remove_vig_two_way(
                            selected_decimal,
                            opposite_decimal,
                        )

                        group_decimal = probability_to_decimal(
                            group_probability
                        )
                        probability_basis = "Two-way no-vig"
                        fair_probability_count += 1

                    elif (
                        pricing_method
                        == "Complete three-way market (remove vig)"
                    ):
                        st.caption(
                            "Use for regulation markets where the selected "
                            "outcome, draw, and opposing outcome cover every "
                            "possible result."
                        )

                        price_col1, price_col2, price_col3 = st.columns(3)

                        if odds_format == "American":
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected outcome",
                                    value=120,
                                    step=5,
                                    key=f"v08_selected_3way_a_{event_index}",
                                )
                            with price_col2:
                                draw_price = st.number_input(
                                    "Draw",
                                    value=240,
                                    step=5,
                                    key=f"v08_selected_3way_d_{event_index}",
                                )
                            with price_col3:
                                opposite_price = st.number_input(
                                    "Other outcome",
                                    value=220,
                                    step=5,
                                    key=f"v08_selected_3way_b_{event_index}",
                                )
                        elif odds_format == "Decimal":
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected decimal",
                                    min_value=1.01,
                                    value=2.20,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_da_{event_index}",
                                )
                            with price_col2:
                                draw_price = st.number_input(
                                    "Draw decimal",
                                    min_value=1.01,
                                    value=3.40,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_dd_{event_index}",
                                )
                            with price_col3:
                                opposite_price = st.number_input(
                                    "Other outcome decimal",
                                    min_value=1.01,
                                    value=3.20,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_db_{event_index}",
                                )
                        else:
                            with price_col1:
                                selected_price = st.number_input(
                                    "Selected listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=45.45,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_pa_{event_index}",
                                )
                            with price_col2:
                                draw_price = st.number_input(
                                    "Draw listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=29.41,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_pd_{event_index}",
                                )
                            with price_col3:
                                opposite_price = st.number_input(
                                    "Other listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=31.25,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_selected_3way_pb_{event_index}",
                                )

                        selected_decimal = convert_input_to_decimal(
                            odds_format,
                            selected_price,
                        )
                        draw_decimal = convert_input_to_decimal(
                            odds_format,
                            draw_price,
                        )
                        opposite_decimal = convert_input_to_decimal(
                            odds_format,
                            opposite_price,
                        )

                        (
                            group_probability,
                            _,
                            _,
                            group_overround,
                        ) = remove_vig_three_way(
                            selected_decimal,
                            draw_decimal,
                            opposite_decimal,
                        )

                        group_decimal = probability_to_decimal(
                            group_probability
                        )
                        probability_basis = "Three-way no-vig"
                        fair_probability_count += 1

                    else:
                        if odds_format == "American":
                            group_price = st.number_input(
                                (
                                    "Exact same-game group odds"
                                    if group_type == "Same-game group"
                                    else "Selected outcome odds"
                                ),
                                value=200,
                                step=5,
                                key=f"v08_group_american_{event_index}",
                            )
                        elif odds_format == "Decimal":
                            group_price = st.number_input(
                                (
                                    "Exact same-game group decimal odds"
                                    if group_type == "Same-game group"
                                    else "Selected outcome decimal odds"
                                ),
                                min_value=1.01,
                                value=3.00,
                                step=0.01,
                                format="%.2f",
                                key=f"v08_group_decimal_{event_index}",
                            )
                        else:
                            group_price = st.number_input(
                                (
                                    "Exact same-game group implied "
                                    "probability (%)"
                                    if group_type == "Same-game group"
                                    else "Selected listed probability (%)"
                                ),
                                min_value=0.01,
                                max_value=99.99,
                                value=33.33,
                                step=0.01,
                                format="%.2f",
                                key=f"v08_group_probability_{event_index}",
                            )

                        group_decimal = convert_input_to_decimal(
                            odds_format,
                            group_price,
                        )
                        group_probability = decimal_to_probability(
                            group_decimal
                        )
                        group_overround = None

                        if group_type == "Same-game group":
                            probability_basis = "Exact SGP implied"
                        else:
                            probability_basis = "Listed implied"

                    event_group_decimals.append(group_decimal)
                    event_group_probabilities.append(group_probability)

                    event_rows.append(
                        {
                            "Event": event_name,
                            "Type": group_type,
                            "Selections": int(selection_count),
                            "Probability basis": probability_basis,
                            "Group probability": (
                                f"{group_probability:.2f}%"
                            ),
                            "Group fair/listed odds": (
                                f"{decimal_to_american(group_decimal):+.0f}"
                            ),
                        }
                    )

                    st.caption(
                        "Selections: " + " • ".join(selection_labels)
                    )

                    if group_overround is not None:
                        st.caption(
                            f"Estimated market overround removed: "
                            f"{group_overround:.2f}%"
                        )

            synthetic_decimal = combine_decimal_odds(
                event_group_decimals
            )
            synthetic_american = decimal_to_american(
                synthetic_decimal
            )
            synthetic_probability = decimal_to_probability(
                synthetic_decimal
            )

            offered_probability = decimal_to_probability(
                offered_ticket_decimal
            )

            price_difference_percent = (
                relative_price_difference_percent(
                    offered_ticket_decimal,
                    synthetic_decimal,
                )
            )

            offered_total_return = calculate_total_return(
                parlay_stake,
                offered_ticket_decimal,
            )

            synthetic_total_return = calculate_total_return(
                parlay_stake,
                synthetic_decimal,
            )

            payout_difference = (
                offered_total_return - synthetic_total_return
            )

            weakest_index = event_group_probabilities.index(
                min(event_group_probabilities)
            )
            weakest_event = event_rows[weakest_index]["Event"]
            weakest_probability = event_group_probabilities[
                weakest_index
            ]

            st.divider()
            st.subheader("Ticket Summary")

            summary_col1, summary_col2, summary_col3, summary_col4 = (
                st.columns(4)
            )

            summary_col1.metric("Events", int(event_count))
            summary_col2.metric("Selections", total_selections)
            summary_col3.metric("Same-game groups", sgp_group_count)
            summary_col4.metric(
                "Standalone selections",
                standalone_count,
            )

            st.dataframe(
                event_rows,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Price Comparison")

            price_col1, price_col2, price_col3 = st.columns(3)

            price_col1.metric(
                "Sportsbook offered odds",
                f"{decimal_to_american(offered_ticket_decimal):+.0f}",
            )
            price_col2.metric(
                "Synthetic component odds",
                f"{synthetic_american:+.0f}",
            )
            price_col3.metric(
                "Offered vs. synthetic price",
                f"{price_difference_percent:+.2f}%",
            )

            payout_col1, payout_col2, payout_col3 = st.columns(3)

            payout_col1.metric(
                "Offered total return",
                f"${offered_total_return:,.2f}",
            )
            payout_col2.metric(
                "Synthetic total return",
                f"${synthetic_total_return:,.2f}",
            )
            payout_col3.metric(
                "Payout difference",
                f"${payout_difference:+,.2f}",
            )

            probability_col1, probability_col2 = st.columns(2)

            probability_col1.metric(
                "Offered implied probability",
                f"{offered_probability:.2f}%",
            )
            probability_col2.metric(
                "Synthetic component probability",
                f"{synthetic_probability:.2f}%",
            )

            if price_difference_percent > 1:
                st.success(
                    "The sportsbook's full-ticket price pays more than the "
                    "price produced by multiplying the entered event-group "
                    "prices."
                )
            elif price_difference_percent < -1:
                st.warning(
                    "The sportsbook's full-ticket price pays less than the "
                    "price produced by multiplying the entered event-group "
                    "prices."
                )
            else:
                st.info(
                    "The sportsbook's full-ticket price is close to the "
                    "synthetic price produced by the event groups."
                )

            st.info(
                f"The lowest-probability event group is "
                f"**{weakest_event}** at {weakest_probability:.2f}%. "
                f"This identifies the group most likely to fail—not "
                f"necessarily the worst-priced group."
            )

            if fair_probability_count < int(event_count):
                st.warning(
                    "At least one event group uses listed or same-game "
                    "implied probability rather than a complete no-vig "
                    "market. Treat the synthetic probability as a pricing "
                    "reference, not a true win probability."
                )
            else:
                st.success(
                    "Every standalone event group was valued with a complete "
                    "market and had its estimated overround removed."
                )


            if fair_probability_count == int(event_count):
                quality_level = "High"
                quality_reasons = [
                    "Every event group used a complete market.",
                    "Estimated overround was removed from every event group.",
                    "Separate events were combined under an independence assumption.",
                ]
            elif fair_probability_count > 0:
                quality_level = "Medium"
                quality_reasons = [
                    "At least one complete market had estimated vig removed.",
                    "At least one group still uses a listed or exact SGP price.",
                    "Separate events were combined under an independence assumption.",
                ]
            else:
                quality_level = "Limited"
                quality_reasons = [
                    "The analysis relies on listed or exact SGP prices.",
                    "Sportsbook margin remains inside at least part of the estimate.",
                    "The result is a price comparison rather than a true probability model.",
                ]

            render_analysis_quality(
                quality_level,
                quality_reasons,
            )

            render_takeaway(
                (
                    "The offered ticket price is better than its components."
                    if price_difference_percent > 1
                    else (
                        "The offered ticket price is worse than its components."
                        if price_difference_percent < -1
                        else "The offered ticket price is close to its components."
                    )
                ),
                (
                    f"The sportsbook offers "
                    f"{decimal_to_american(offered_ticket_decimal):+.0f}, "
                    f"while the entered event groups combine to approximately "
                    f"{synthetic_american:+.0f}. The resulting total-return "
                    f"difference is ${payout_difference:+,.2f}."
                ),
                (
                    "Same-game group prices may still include sportsbook "
                    "margin, and separate events are assumed independent."
                ),
            )

            with st.expander("How PositionIQ handled this ticket"):
                st.markdown(
                    """
                    - Every event is treated as one event group.
                    - Multiple selections from the same event use one exact
                      same-game group price.
                    - Standalone selections can use complete two-way or
                      three-way markets to remove estimated vig.
                    - Separate event groups are multiplied under an
                      independence assumption.
                    - The offered full-ticket price is compared with the
                      synthetic price created from the entered groups.

                    The synthetic result is a pricing benchmark. It is not
                    automatically a prediction of the ticket's true chance
                    of winning.
                    """
                )

        except ValueError as error:
            st.error(str(error))

    # -----------------------------------------------------
    # LIVE TICKET AND CASHOUT
    # -----------------------------------------------------

    with live_tab:
        st.subheader("Live Ticket and Cashout")

        st.caption(
            "Recreate only the remaining uncertainty. Won events no longer "
            "reduce the ticket's chance of finishing; lost events make the "
            "ticket worth zero; voids should be reflected in the sportsbook's "
            "updated total payout."
        )

        try:
            live_col1, live_col2, live_col3 = st.columns(3)

            with live_col1:
                live_original_stake = st.number_input(
                    "Original ticket stake ($)",
                    min_value=0.01,
                    value=25.00,
                    step=5.00,
                    format="%.2f",
                    key="v08_live_stake",
                )

            with live_col2:
                live_total_payout = st.number_input(
                    "Current total payout if ticket wins ($)",
                    min_value=0.01,
                    value=500.00,
                    step=25.00,
                    format="%.2f",
                    key="v08_live_total_payout",
                    help=(
                        "Use the sportsbook's updated payout after any voids "
                        "or odds adjustments."
                    ),
                )

            with live_col3:
                live_cashout_offer = st.number_input(
                    "Current cashout offer ($)",
                    min_value=0.00,
                    value=175.00,
                    step=5.00,
                    format="%.2f",
                    key="v08_live_cashout_offer",
                )

            live_event_count = st.number_input(
                "Number of events on the original ticket",
                min_value=1,
                max_value=8,
                value=3,
                step=1,
                key="v08_live_event_count",
            )

            remaining_probabilities = []
            active_event_names = []
            lost_ticket = False
            won_count = 0
            void_count = 0

            for event_index in range(int(live_event_count)):
                with st.expander(
                    f"Live event {event_index + 1}",
                    expanded=(event_index == 0),
                ):
                    live_event_name = st.text_input(
                        "Event name",
                        value="",
                        placeholder="Example: Chiefs vs Bills",
                        key=f"v08_live_event_name_{event_index}",
                    ).strip() or f"Event {event_index + 1}"

                    live_group_type = st.radio(
                        "Event-group type",
                        [
                            "Standalone selection",
                            "Same-game group",
                        ],
                        horizontal=True,
                        key=f"v08_live_group_type_{event_index}",
                    )

                    live_status = st.selectbox(
                        "Status",
                        [
                            "Not started",
                            "Live",
                            "Won",
                            "Lost",
                            "Void",
                        ],
                        key=f"v08_live_status_{event_index}",
                    )

                    if live_status == "Won":
                        won_count += 1
                        st.success(
                            "This event is settled as a win and adds no "
                            "remaining uncertainty."
                        )
                        continue

                    if live_status == "Void":
                        void_count += 1
                        st.info(
                            "This event is void. Confirm that the total payout "
                            "above reflects the sportsbook's adjustment."
                        )
                        continue

                    if live_status == "Lost":
                        lost_ticket = True
                        st.error(
                            "This event lost, so the ticket has no remaining "
                            "cash value unless the sportsbook has a special "
                            "promotion or insurance rule."
                        )
                        continue

                    if live_group_type == "Standalone selection":
                        live_pricing_method = st.selectbox(
                            "Current pricing method",
                            [
                                "Complete two-way market (remove vig)",
                                "Complete three-way market (remove vig)",
                                "Selected price only",
                            ],
                            key=f"v08_live_pricing_{event_index}",
                        )
                    else:
                        live_pricing_method = "Exact current same-game group price"

                    live_odds_format = st.selectbox(
                        "Current odds format",
                        [
                            "American",
                            "Decimal",
                            "Implied probability",
                        ],
                        key=f"v08_live_format_{event_index}",
                    )

                    if (
                        live_pricing_method
                        == "Complete two-way market (remove vig)"
                    ):
                        market_col1, market_col2 = st.columns(2)

                        if live_odds_format == "American":
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket outcome current odds",
                                    value=-150,
                                    step=5,
                                    key=f"v08_live_2way_a_{event_index}",
                                )
                            with market_col2:
                                live_opposite = st.number_input(
                                    "Opposite outcome current odds",
                                    value=130,
                                    step=5,
                                    key=f"v08_live_2way_b_{event_index}",
                                )
                        elif live_odds_format == "Decimal":
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket outcome current decimal",
                                    min_value=1.01,
                                    value=1.67,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_2way_da_{event_index}",
                                )
                            with market_col2:
                                live_opposite = st.number_input(
                                    "Opposite outcome current decimal",
                                    min_value=1.01,
                                    value=2.30,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_2way_db_{event_index}",
                                )
                        else:
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket outcome listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=60.00,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_2way_pa_{event_index}",
                                )
                            with market_col2:
                                live_opposite = st.number_input(
                                    "Opposite listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=43.48,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_2way_pb_{event_index}",
                                )

                        live_selected_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_selected,
                        )
                        live_opposite_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_opposite,
                        )

                        (
                            live_group_probability,
                            _,
                            live_overround,
                        ) = remove_vig_two_way(
                            live_selected_decimal,
                            live_opposite_decimal,
                        )

                        st.caption(
                            f"Current overround removed: "
                            f"{live_overround:.2f}%"
                        )

                    elif (
                        live_pricing_method
                        == "Complete three-way market (remove vig)"
                    ):
                        market_col1, market_col2, market_col3 = st.columns(3)

                        if live_odds_format == "American":
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket outcome",
                                    value=120,
                                    step=5,
                                    key=f"v08_live_3way_a_{event_index}",
                                )
                            with market_col2:
                                live_draw = st.number_input(
                                    "Draw",
                                    value=240,
                                    step=5,
                                    key=f"v08_live_3way_d_{event_index}",
                                )
                            with market_col3:
                                live_opposite = st.number_input(
                                    "Other outcome",
                                    value=220,
                                    step=5,
                                    key=f"v08_live_3way_b_{event_index}",
                                )
                        elif live_odds_format == "Decimal":
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket outcome decimal",
                                    min_value=1.01,
                                    value=2.20,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_da_{event_index}",
                                )
                            with market_col2:
                                live_draw = st.number_input(
                                    "Draw decimal",
                                    min_value=1.01,
                                    value=3.40,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_dd_{event_index}",
                                )
                            with market_col3:
                                live_opposite = st.number_input(
                                    "Other outcome decimal",
                                    min_value=1.01,
                                    value=3.20,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_db_{event_index}",
                                )
                        else:
                            with market_col1:
                                live_selected = st.number_input(
                                    "Ticket listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=45.45,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_pa_{event_index}",
                                )
                            with market_col2:
                                live_draw = st.number_input(
                                    "Draw listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=29.41,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_pd_{event_index}",
                                )
                            with market_col3:
                                live_opposite = st.number_input(
                                    "Other listed probability (%)",
                                    min_value=0.01,
                                    max_value=99.99,
                                    value=31.25,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"v08_live_3way_pb_{event_index}",
                                )

                        live_selected_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_selected,
                        )
                        live_draw_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_draw,
                        )
                        live_opposite_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_opposite,
                        )

                        (
                            live_group_probability,
                            _,
                            _,
                            live_overround,
                        ) = remove_vig_three_way(
                            live_selected_decimal,
                            live_draw_decimal,
                            live_opposite_decimal,
                        )

                        st.caption(
                            f"Current overround removed: "
                            f"{live_overround:.2f}%"
                        )

                    else:
                        if live_odds_format == "American":
                            live_group_price = st.number_input(
                                (
                                    "Exact current same-game group odds"
                                    if live_group_type == "Same-game group"
                                    else "Ticket outcome current odds"
                                ),
                                value=150,
                                step=5,
                                key=f"v08_live_group_a_{event_index}",
                            )
                        elif live_odds_format == "Decimal":
                            live_group_price = st.number_input(
                                (
                                    "Exact current same-game group decimal"
                                    if live_group_type == "Same-game group"
                                    else "Ticket outcome current decimal"
                                ),
                                min_value=1.01,
                                value=2.50,
                                step=0.01,
                                format="%.2f",
                                key=f"v08_live_group_d_{event_index}",
                            )
                        else:
                            live_group_price = st.number_input(
                                (
                                    "Exact current same-game group implied "
                                    "probability (%)"
                                    if live_group_type == "Same-game group"
                                    else "Ticket outcome listed probability (%)"
                                ),
                                min_value=0.01,
                                max_value=99.99,
                                value=40.00,
                                step=0.01,
                                format="%.2f",
                                key=f"v08_live_group_p_{event_index}",
                            )

                        live_group_decimal = convert_input_to_decimal(
                            live_odds_format,
                            live_group_price,
                        )
                        live_group_probability = decimal_to_probability(
                            live_group_decimal
                        )

                    remaining_probabilities.append(
                        live_group_probability
                    )
                    active_event_names.append(live_event_name)

            if lost_ticket:
                remaining_ticket_probability = 0.0
                estimated_live_value = 0.0
                cashout_difference = live_cashout_offer
                offer_percentage = 0.0
                cashout_break_even = (
                    cashout_break_even_probability(
                        live_cashout_offer,
                        live_total_payout,
                    )
                )
            elif remaining_probabilities:
                remaining_ticket_probability = (
                    combine_independent_probabilities(
                        remaining_probabilities
                    )
                )
                estimated_live_value = fair_cashout_value(
                    live_total_payout,
                    remaining_ticket_probability,
                )
                cashout_difference = cashout_value_difference(
                    live_cashout_offer,
                    estimated_live_value,
                )
                offer_percentage = cashout_offer_percentage(
                    live_cashout_offer,
                    estimated_live_value,
                )
                cashout_break_even = (
                    cashout_break_even_probability(
                        live_cashout_offer,
                        live_total_payout,
                    )
                )
            else:
                remaining_ticket_probability = 100.0
                estimated_live_value = live_total_payout
                cashout_difference = cashout_value_difference(
                    live_cashout_offer,
                    estimated_live_value,
                )
                offer_percentage = cashout_offer_percentage(
                    live_cashout_offer,
                    estimated_live_value,
                )
                cashout_break_even = (
                    cashout_break_even_probability(
                        live_cashout_offer,
                        live_total_payout,
                    )
                )

            st.divider()
            st.subheader("Live Ticket Valuation")

            status_col1, status_col2, status_col3 = st.columns(3)

            status_col1.metric("Won events", won_count)
            status_col2.metric("Voided events", void_count)
            status_col3.metric(
                "Active or upcoming events",
                len(remaining_probabilities),
            )

            value_col1, value_col2, value_col3 = st.columns(3)

            value_col1.metric(
                "Remaining ticket probability",
                f"{remaining_ticket_probability:.2f}%",
            )
            value_col2.metric(
                "Estimated current ticket value",
                f"${estimated_live_value:,.2f}",
            )
            value_col3.metric(
                "Cashout offer",
                f"${live_cashout_offer:,.2f}",
            )

            compare_col1, compare_col2, compare_col3 = st.columns(3)

            compare_col1.metric(
                "Offer vs. estimated value",
                f"${cashout_difference:+,.2f}",
            )
            compare_col2.metric(
                "Offer as % of estimated value",
                (
                    f"{offer_percentage:.2f}%"
                    if estimated_live_value > 0
                    else "N/A"
                ),
            )
            compare_col3.metric(
                "Cashout break-even probability",
                f"{cashout_break_even:.2f}%",
            )

            if lost_ticket:
                st.error(
                    "At least one event is marked lost. Standard ticket "
                    "valuation is zero unless a sportsbook promotion changes "
                    "the settlement."
                )
            elif remaining_ticket_probability > cashout_break_even:
                st.info(
                    "The market-based remaining probability is above the "
                    "cashout break-even threshold, so continuing has the "
                    "higher estimated value. It still carries the risk of "
                    "losing the cashout offer."
                )
            elif remaining_ticket_probability < cashout_break_even:
                st.info(
                    "The market-based remaining probability is below the "
                    "cashout break-even threshold, so accepting the offer has "
                    "the higher estimated value under the entered prices."
                )
            else:
                st.info(
                    "The remaining probability is approximately equal to the "
                    "cashout break-even threshold."
                )

            if active_event_names:
                st.caption(
                    "Remaining event groups: "
                    + " • ".join(active_event_names)
                )

            with st.expander("Live valuation limitations"):
                st.markdown(
                    """
                    - Same-game groups require an exact current group price.
                    - Event groups are assumed independent across separate
                      events.
                    - Listed-only prices still contain sportsbook margin.
                    - Live prices can change quickly.
                    - A void must be reflected in the current total payout.
                    - Cashout decisions also depend on personal risk tolerance,
                      not only estimated value.
                    """
                )

        except ValueError as error:
            st.error(str(error))

    # -----------------------------------------------------
    # FINAL-LEG HEDGE
    # -----------------------------------------------------

    with final_leg_tab:
        st.subheader("Final-Leg Parlay Hedge")

        st.warning(
            "Use this only when exactly one two-way event group remains and "
            "the hedge outcome is the exact opposite of the remaining ticket "
            "outcome. A three-way regulation market requires coverage of all "
            "remaining outcomes."
        )

        try:
            final_col1, final_col2 = st.columns(2)

            with final_col1:
                final_original_stake = st.number_input(
                    "Original parlay stake ($)",
                    min_value=0.01,
                    value=25.00,
                    step=5.00,
                    format="%.2f",
                    key="v08_final_original_stake",
                )

            with final_col2:
                final_total_payout = st.number_input(
                    "Total parlay payout if final event wins ($)",
                    min_value=0.01,
                    value=500.00,
                    step=25.00,
                    format="%.2f",
                    key="v08_final_total_payout",
                )

            final_hedge_format = st.selectbox(
                "Opposing hedge odds format",
                [
                    "American",
                    "Decimal",
                    "Fractional",
                    "Implied probability",
                ],
                key="v08_final_hedge_format",
            )

            if final_hedge_format == "American":
                final_hedge_input = st.number_input(
                    "Opposing hedge American odds",
                    value=150,
                    step=5,
                    key="v08_final_hedge_american",
                )
            elif final_hedge_format == "Decimal":
                final_hedge_input = st.number_input(
                    "Opposing hedge decimal odds",
                    min_value=1.01,
                    value=2.50,
                    step=0.01,
                    format="%.2f",
                    key="v08_final_hedge_decimal",
                )
            elif final_hedge_format == "Fractional":
                final_hedge_input = st.text_input(
                    "Opposing hedge fractional odds",
                    value="3/2",
                    key="v08_final_hedge_fractional",
                )
            else:
                final_hedge_input = st.number_input(
                    "Opposing hedge implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=40.00,
                    step=0.01,
                    format="%.2f",
                    key="v08_final_hedge_probability",
                )

            final_hedge_decimal = convert_input_to_decimal(
                final_hedge_format,
                final_hedge_input,
            )

            equal_profit_hedge = parlay_final_leg_equal_profit_hedge(
                final_total_payout,
                final_hedge_decimal,
            )

            final_strategy = st.selectbox(
                "Hedge goal",
                [
                    "Equal profit either way",
                    "Hedge most of the equal-profit amount",
                    "Hedge half of the equal-profit amount",
                    "Hedge a small portion",
                    "Choose my own amount",
                ],
                key="v08_final_strategy",
            )

            if final_strategy == "Equal profit either way":
                selected_final_hedge = equal_profit_hedge
            elif (
                final_strategy
                == "Hedge most of the equal-profit amount"
            ):
                selected_final_hedge = equal_profit_hedge * 0.75
            elif (
                final_strategy
                == "Hedge half of the equal-profit amount"
            ):
                selected_final_hedge = equal_profit_hedge * 0.50
            elif final_strategy == "Hedge a small portion":
                selected_final_hedge = equal_profit_hedge * 0.25
            else:
                selected_final_hedge = st.number_input(
                    "Custom hedge amount ($)",
                    min_value=0.00,
                    value=100.00,
                    step=10.00,
                    format="%.2f",
                    key="v08_final_custom_hedge",
                )

            (
                profit_if_parlay_wins,
                profit_if_hedge_wins,
            ) = parlay_final_leg_outcomes(
                final_original_stake,
                final_total_payout,
                selected_final_hedge,
                final_hedge_decimal,
            )

            guaranteed_final_result = min(
                profit_if_parlay_wins,
                profit_if_hedge_wins,
            )

            st.divider()
            st.subheader("Final-Leg Hedge Results")

            hedge_result_col1, hedge_result_col2 = st.columns(2)

            hedge_result_col1.metric(
                "Equal-profit hedge amount",
                f"${equal_profit_hedge:,.2f}",
            )

            hedge_result_col2.metric(
                "Selected hedge amount",
                f"${selected_final_hedge:,.2f}",
            )

            outcome_col1, outcome_col2 = st.columns(2)

            with outcome_col1:
                st.markdown("#### Parlay final event wins")
                st.metric(
                    "Net ticket profit",
                    f"${profit_if_parlay_wins:,.2f}",
                )

            with outcome_col2:
                st.markdown("#### Opposing hedge wins")
                st.metric(
                    "Net combined profit",
                    f"${profit_if_hedge_wins:,.2f}",
                )

            if guaranteed_final_result > 0:
                st.success(
                    f"This setup guarantees at least "
                    f"${guaranteed_final_result:,.2f} in net profit."
                )
            elif abs(guaranteed_final_result) < 0.005:
                st.info(
                    "This setup approximately eliminates the worst-case loss."
                )
            else:
                st.warning(
                    f"One outcome still produces a loss of "
                    f"${abs(guaranteed_final_result):,.2f}."
                )

        except ValueError as error:
            st.error(str(error))

st.divider()
st.caption(
    "PositionIQ v0.9 — Beginner guidance, advanced methodology, analysis "
    "quality ratings, sensitivity analysis, and clearer takeaways."
)
