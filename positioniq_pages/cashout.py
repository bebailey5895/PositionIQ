import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

st.header("Cashout Analyzer")

render_tool_intro(
    "Is the sportsbook's cashout offer above or below the ticket's "
    "estimated current value?",
    "This compares expected value and certainty. It does not make the "
    "risk decision for the user.",
)


example_col1, example_col2 = st.columns(2)

with example_col1:
    if st.button("Load cashout example", key="cashout_example"):
        st.session_state["cashout_original_format"] = "American"
        st.session_state["cashout_original_stake"] = 100.00
        st.session_state["cashout_offer"] = 180.00
        st.session_state["cashout_original_american"] = 200
        st.session_state["cashout_probability_method"] = (
            "Enter my own probability"
        )
        st.session_state["cashout_manual_probability"] = 65.00
        st.rerun()

with example_col2:
    if st.button("Reset cashout tool", key="reset_cashout"):
        reset_keys(
            [
                key
                for key in list(st.session_state.keys())
                if key.startswith("cashout_")
            ]
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

    with st.expander("How was this calculated?", expanded=advanced_mode):
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

    with st.expander("Important limitations", expanded=advanced_mode):
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
