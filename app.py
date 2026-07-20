import streamlit as st

from calculations import (
    american_to_decimal,
    calculate_profit,
    calculate_total_return,
    decimal_to_american,
    decimal_to_fractional,
    decimal_to_probability,
    fractional_to_decimal,
    probability_to_decimal,
    remove_vig_two_way,
)


st.set_page_config(
    page_title="PositionIQ",
    page_icon="📊",
    layout="centered",
)

def get_margin_rating(
    market_margin,
):

    if market_margin < 0:
        return (
            "🟢",
            "Potential Arbitrage",
            "Combined probability is below 100%."
        )

    if market_margin < 2:
        return (
            "🟢",
            "Very Low Margin",
            "Highly competitive pricing."
        )

    if market_margin < 4:
        return (
            "🟢",
            "Competitive Pricing",
            "Relatively low market margin."
        )

    if market_margin < 6:
        return (
            "🟡",
            "Typical Pricing",
            "Common sportsbook pricing."
        )

    if market_margin < 8:
        return (
            "🟠",
            "Expensive Pricing",
            "Higher than average market margin."
        )

    return (
        "🔴",
        "Very Expensive Pricing",
        "Substantial sportsbook margin."
    )

st.title("PositionIQ")
st.caption("Understand every possible outcome.")

converter_tab, no_vig_tab = st.tabs(
    [
        "Odds Converter",
        "No-Vig Calculator",
    ]
)


# =========================================================
# ODDS CONVERTER
# =========================================================

with converter_tab:
    st.header("Universal Odds Converter")

    st.write(
        "Convert American, decimal, fractional, and "
        "implied-probability odds."
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
                help="Examples: +120 or -120",
                key="converter_american",
            )

            decimal_odds = american_to_decimal(
                float(entered_odds)
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

            decimal_odds = float(entered_odds)

        elif odds_format == "Fractional":
            entered_odds = st.text_input(
                "Enter fractional odds",
                value="6/5",
                help="Examples: 6/5, 5/2, or 10/1",
                key="converter_fractional",
            )

            decimal_odds = fractional_to_decimal(
                entered_odds
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

            decimal_odds = probability_to_decimal(
                float(entered_odds)
            )

        american_odds = decimal_to_american(
            decimal_odds
        )

        fractional_odds = decimal_to_fractional(
            decimal_odds
        )

        implied_probability = decimal_to_probability(
            decimal_odds
        )

        st.divider()
        st.subheader("Converted odds")

        col1, col2 = st.columns(2)

        col1.metric(
            "American",
            f"{american_odds:+.0f}",
        )

        col2.metric(
            "Decimal",
            f"{decimal_odds:.4f}",
        )

        col3, col4 = st.columns(2)

        col3.metric(
            "Fractional",
            fractional_odds,
        )

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

        net_profit = calculate_profit(
            stake,
            decimal_odds,
        )

        total_return = calculate_total_return(
            stake,
            decimal_odds,
        )

        payout_col1, payout_col2 = st.columns(2)

        payout_col1.metric(
            "Net profit",
            f"${net_profit:,.2f}",
        )

        payout_col2.metric(
            "Total return",
            f"${total_return:,.2f}",
        )

        st.info(
            "Net profit excludes your original stake. "
            "Total return includes it."
        )

    except ValueError as error:
        st.error(str(error))

    st.divider()

    with st.expander(
        "Learn About American Odds, Vig, and No-Vig Markets"
    ):
        st.markdown(
            """
### American odds

**Positive odds** show the profit produced by a $100 stake.

For example, `+120` means:

- Stake: $100
- Net profit: $120
- Total return: $220
- Implied probability: approximately 45.45%

**Negative odds** show how much must be risked to make $100 in profit.

For example, `-120` means:

- Stake: $120
- Net profit: $100
- Total return: $220
- Implied probability: approximately 54.55%

Although `+120` and `-120` contain the same number, they represent
different prices, probabilities, and payouts.

---

### What is vig?

Vig, short for vigorish, is the sportsbook's built-in pricing advantage.

Consider a two-outcome market:

- Team A: `-110`
- Team B: `-110`

Each side has an implied probability of approximately 52.38%.

Together:

- 52.38% + 52.38% = 104.76%

The outcomes should theoretically total 100%. The extra 4.76 percentage
points represent the market's overround or built-in margin.

---

### Vig, overround, and hold

These terms are closely related but are not always identical.

- **Vig** refers to the sportsbook's built-in commission or pricing edge.
- **Overround** is how far the combined implied probabilities exceed 100%.
- **Hold** usually refers to the sportsbook's actual retained revenue after
  wagers are settled.

PositionIQ currently calculates the estimated theoretical market margin
from the entered prices.

---

### What is no-vig?

A no-vig calculation removes the sportsbook's estimated margin.

It adjusts the listed implied probabilities so they add up to exactly 100%.

For example:

- Team A: `-120`
- Team B: `+105`

The raw implied probabilities total more than 100%. PositionIQ
proportionally normalizes them to estimate:

- Fair probability for Team A
- Fair probability for Team B
- Fair American and decimal prices

No-vig probabilities reflect the market's pricing after removing the
estimated margin. They are not predictions of the actual result.

---

### Important limitation

Sportsbook prices can reflect:

- Margin
- Betting demand
- Risk management
- Public behavior
- New information
- Market liquidity

No-vig calculations estimate fair market prices based on the entered odds.
They do not guarantee value or predict which outcome will win.
            """
        )


# =========================================================
# TWO-WAY NO-VIG CALCULATOR
# =========================================================

with no_vig_tab:
    st.header("Two-Way No-Vig Calculator")

    st.write(
        "Enter both sides of a two-outcome market to estimate "
        "the sportsbook margin and fair no-vig prices."
    )

    odds_format = st.selectbox(
        "Input format",
        [
            "American",
            "Decimal",
            "Implied probability",
        ],
        key="no_vig_format",
    )

    name_col1, name_col2 = st.columns(2)

    with name_col1:
        side_a_name = st.text_input(
            "First outcome",
            value="Team A",
            key="side_a_name",
        )

    with name_col2:
        side_b_name = st.text_input(
            "Second outcome",
            value="Team B",
            key="side_b_name",
        )

    try:
        input_col1, input_col2 = st.columns(2)

        if odds_format == "American":
            with input_col1:
                side_a_input = st.number_input(
                    f"{side_a_name} American odds",
                    value=-120,
                    step=5,
                    key="side_a_american",
                )

            with input_col2:
                side_b_input = st.number_input(
                    f"{side_b_name} American odds",
                    value=105,
                    step=5,
                    key="side_b_american",
                )

            side_a_decimal = american_to_decimal(
                float(side_a_input)
            )

            side_b_decimal = american_to_decimal(
                float(side_b_input)
            )

        elif odds_format == "Decimal":
            with input_col1:
                side_a_input = st.number_input(
                    f"{side_a_name} decimal odds",
                    min_value=1.01,
                    value=1.83,
                    step=0.01,
                    format="%.2f",
                    key="side_a_decimal",
                )

            with input_col2:
                side_b_input = st.number_input(
                    f"{side_b_name} decimal odds",
                    min_value=1.01,
                    value=2.05,
                    step=0.01,
                    format="%.2f",
                    key="side_b_decimal",
                )

            side_a_decimal = float(side_a_input)
            side_b_decimal = float(side_b_input)

        else:
            with input_col1:
                side_a_input = st.number_input(
                    f"{side_a_name} implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=54.55,
                    step=0.01,
                    format="%.2f",
                    key="side_a_probability",
                )

            with input_col2:
                side_b_input = st.number_input(
                    f"{side_b_name} implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=48.78,
                    step=0.01,
                    format="%.2f",
                    key="side_b_probability",
                )

            side_a_decimal = probability_to_decimal(
                float(side_a_input)
            )

            side_b_decimal = probability_to_decimal(
                float(side_b_input)
            )

        side_a_raw_probability = decimal_to_probability(
            side_a_decimal
        )

        side_b_raw_probability = decimal_to_probability(
            side_b_decimal
        )

        (
            side_a_fair_probability,
            side_b_fair_probability,
            market_margin,
        ) = remove_vig_two_way(
            side_a_decimal,
            side_b_decimal,
        )

        side_a_fair_decimal = probability_to_decimal(
            side_a_fair_probability
        )

        side_b_fair_decimal = probability_to_decimal(
            side_b_fair_probability
        )

        side_a_fair_american = decimal_to_american(
            side_a_fair_decimal
        )

        side_b_fair_american = decimal_to_american(
            side_b_fair_decimal
        )

        combined_probability = (
            side_a_raw_probability
            + side_b_raw_probability
        )

        st.divider()
        st.subheader("Market analysis")

        analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

        analysis_col1.metric(
            "Combined probability",
            f"{combined_probability:.2f}%",
        )

        analysis_col2.metric(
            "Estimated overround",
            f"{market_margin:.2f}%",
        )

        analysis_col3.metric(
            "No-vig total",
            "100.00%",
        )

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
                "Confirm that all possible outcomes are covered and that "
                "both prices remain available."
            )

        elif market_margin < 2:
            st.success(
                "This market is priced very competitively. Small differences "
                "in price can become meaningful across many wagers."
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
                "This market is more expensive than many standard two-way "
                "markets. Consider comparing prices elsewhere."
            )

        else:
            st.error(
                "This is a high-margin market. Props, futures, and same-game "
                "parlays often contain larger pricing margins."
            )

        with st.expander("What does this mean?"):
            st.markdown(
                f"""
                ### Current Market Summary

                - Combined probability: **{combined_probability:.2f}%**
                - Estimated overround: **{market_margin:.2f}%**
                - Pricing rating: **{rating_icon} {rating_label}**

                ### Pricing Guide

                - Under 2%: Very low margin
                - 2% to 4%: Competitive
                - 4% to 6%: Typical
                - 6% to 8%: Expensive
                - Above 8%: Very expensive

                ### Why This Matters

                The implied probabilities for every possible outcome should
                theoretically add up to 100%.

                When they total more than 100%, the excess represents the
                market's estimated overround. Lower overround generally means
                better pricing for the bettor.

                PositionIQ removes this estimated margin proportionally to
                calculate the fair no-vig probabilities shown below.
                """
            )

        with st.expander(
            "Useful details bettors often overlook",
            expanded=False,
        ):
            st.markdown(
                """
                **Small price differences matter**

                The difference between -110 and -115 may look minor on one
                wager, but it can materially affect results across hundreds
                of wagers.

                **Overround is not actual sportsbook hold**

                PositionIQ calculates theoretical overround from the entered
                prices. Actual sportsbook hold depends on how money is
                distributed and how wagers settle.

                **No-vig odds are not predictions**

                Fair odds estimate the market price after removing the
                sportsbook's margin. They do not prove that the market's
                underlying probabilities are correct.

                **Shopping for better odds helps**

                Comparing sportsbooks is one of the simplest ways to reduce
                the cost of betting without changing which outcome you select.
                """
            )

        st.divider()
        st.subheader("No-vig estimates")

        result_col1, result_col2 = st.columns(2)

        with result_col1:
            st.markdown(f"### {side_a_name}")

            st.metric(
                "Listed implied probability",
                f"{side_a_raw_probability:.2f}%",
            )

            st.metric(
                "No-vig probability",
                f"{side_a_fair_probability:.2f}%",
            )

            st.metric(
                "Fair American odds",
                f"{side_a_fair_american:+.0f}",
            )

            st.metric(
                "Fair decimal odds",
                f"{side_a_fair_decimal:.4f}",
            )

        with result_col2:
            st.markdown(f"### {side_b_name}")

            st.metric(
                "Listed implied probability",
                f"{side_b_raw_probability:.2f}%",
            )

            st.metric(
                "No-vig probability",
                f"{side_b_fair_probability:.2f}%",
            )

            st.metric(
                "Fair American odds",
                f"{side_b_fair_american:+.0f}",
            )

            st.metric(
                "Fair decimal odds",
                f"{side_b_fair_decimal:.4f}",
            )

        st.caption(
            "PositionIQ uses proportional normalization to remove the "
            "estimated overround. Other no-vig methods may produce slightly "
            "different results, particularly in heavily skewed markets."
        )

    except ValueError as error:
        st.error(str(error))


st.divider()

st.caption(
    "PositionIQ v0.3 — Odds conversion, payout analysis, "
    "and two-way no-vig calculations."
)