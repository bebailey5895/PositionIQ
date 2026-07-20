import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

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


if st.session_state.parlay_workspace:
    workspace = st.session_state.parlay_workspace

    with st.container(border=True):
        st.markdown("#### Active Parlay Workspace")
        st.write(
            f"**{workspace['ticket_name']}** · "
            f"{workspace['event_count']} events · "
            f"{workspace['total_selections']} selections"
        )
        st.caption(
            f"Stake: ${workspace['stake']:,.2f} · "
            f"Original odds: {workspace['offered_american']:+.0f} · "
            f"Potential payout: ${workspace['offered_total_return']:,.2f}"
        )

        clear_workspace = st.button(
            "Clear saved workspace",
            key="clear_parlay_workspace",
        )

        if clear_workspace:
            st.session_state.parlay_workspace = None
            st.rerun()
else:
    st.caption(
        "Build a ticket below and save it to the workspace. The saved "
        "stake, original price, payout, and event structure will carry "
        "into the live, line-movement, and hedge tools."
    )

builder_tab, live_tab, line_movement_tab, final_leg_tab = st.tabs(
    [
        "Ticket Builder",
        "Live Ticket & Cashout",
        "Line Movement / CLV",
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
        ticket_name = st.text_input(
            "Ticket name",
            value="",
            placeholder="Example: World Cup futures parlay",
            key="v12_ticket_name",
        ).strip() or "Untitled parlay"

        sportsbook_name = st.text_input(
            "Sportsbook (optional)",
            value="",
            placeholder="Example: DraftKings",
            key="v12_sportsbook_name",
        ).strip()

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


        if parlay_stake > 10000:
            st.warning(
                "This is an unusually large stake. Confirm that the "
                "amount was entered correctly."
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


        if int(event_count) > 1:
            st.markdown("### Remove-One-Event Comparison")
            st.caption(
                "See how the component-based price and total return change "
                "when each event group is removed."
            )

            removal_rows = []

            for remove_index, event_row in enumerate(event_rows):
                remaining_decimals = [
                    decimal_value
                    for index, decimal_value in enumerate(
                        event_group_decimals
                    )
                    if index != remove_index
                ]

                revised_decimal = combine_decimal_odds(
                    remaining_decimals
                )
                revised_probability = decimal_to_probability(
                    revised_decimal
                )
                revised_return = calculate_total_return(
                    parlay_stake,
                    revised_decimal,
                )

                removal_rows.append(
                    {
                        "Remove event": event_row["Event"],
                        "Revised component odds": (
                            f"{decimal_to_american(revised_decimal):+.0f}"
                        ),
                        "Revised implied probability": (
                            revised_probability
                        ),
                        "Revised total return": revised_return,
                        "Return reduction": (
                            synthetic_total_return - revised_return
                        ),
                    }
                )

            st.dataframe(
                removal_rows,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Revised implied probability": (
                        st.column_config.NumberColumn(
                            format="%.2f%%"
                        )
                    ),
                    "Revised total return": (
                        st.column_config.NumberColumn(
                            format="$%.2f"
                        )
                    ),
                    "Return reduction": (
                        st.column_config.NumberColumn(
                            format="$%.2f"
                        )
                    ),
                },
            )

            if experience_level == "Beginner":
                st.caption(
                    "Removing an event usually lowers the payout but "
                    "raises the chance that every remaining event wins."
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

        share_summary = (
            f"PositionIQ Parlay Analysis\n"
            f"Ticket: {ticket_name}\n"
            f"Offered odds: "
            f"{decimal_to_american(offered_ticket_decimal):+.0f}\n"
            f"Component-based odds: {synthetic_american:+.0f}\n"
            f"Payout difference: ${payout_difference:+,.2f}\n"
            f"Events: {int(event_count)} | "
            f"Selections: {int(total_selections)}"
        )

        with st.expander("Shareable analysis summary"):
            st.code(share_summary, language=None)

        workspace_payload = {
            "ticket_name": ticket_name,
            "sportsbook": sportsbook_name,
            "stake": float(parlay_stake),
            "event_count": int(event_count),
            "total_selections": int(total_selections),
            "same_game_groups": int(sgp_group_count),
            "standalone_selections": int(standalone_count),
            "offered_decimal": float(offered_ticket_decimal),
            "offered_american": float(
                decimal_to_american(offered_ticket_decimal)
            ),
            "offered_total_return": float(offered_total_return),
            "synthetic_decimal": float(synthetic_decimal),
            "synthetic_american": float(synthetic_american),
            "synthetic_probability": float(synthetic_probability),
            "event_groups": event_rows,
        }

        workspace_col1, workspace_col2 = st.columns(2)

        with workspace_col1:
            if st.button(
                "Save ticket to Parlay Workspace",
                type="primary",
                key="save_parlay_workspace",
            ):
                st.session_state.parlay_workspace = workspace_payload
                st.success(
                    "Ticket saved. Its core details now carry into the "
                    "other Parlay Lab tools."
                )

        with workspace_col2:
            export_json = json.dumps(
                workspace_payload,
                indent=2,
            )

            st.download_button(
                "Download ticket JSON",
                data=export_json,
                file_name="positioniq_parlay_ticket.json",
                mime="application/json",
                key="download_parlay_json",
            )

        st.caption(
            "The workspace stores the ticket for the current browser "
            "session. The JSON download can be kept and imported in a "
            "future persistence release."
        )

        with st.expander("How PositionIQ handled this ticket", expanded=advanced_mode):
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

    if st.session_state.parlay_workspace:
        st.success("Saved workspace values prefill the original stake, payout, and event count.")


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
                value=(
                    float(st.session_state.parlay_workspace["stake"])
                    if st.session_state.parlay_workspace
                    else 25.00
                ),
                step=5.00,
                format="%.2f",
                key="v08_live_stake",
            )

        with live_col2:
            live_total_payout = st.number_input(
                "Current total payout if ticket wins ($)",
                min_value=0.01,
                value=(
                    float(
                        st.session_state.parlay_workspace[
                            "offered_total_return"
                        ]
                    )
                    if st.session_state.parlay_workspace
                    else 500.00
                ),
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
            value=(
                int(st.session_state.parlay_workspace["event_count"])
                if st.session_state.parlay_workspace
                else 3
            ),
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
# LINE MOVEMENT / CLV
# -----------------------------------------------------

with line_movement_tab:
    st.subheader("Parlay Line Movement and CLV")

    if st.session_state.parlay_workspace:
        st.success("Saved workspace values prefill the original ticket price and stake.")


    render_tool_intro(
        "Did I lock in a better or worse price than the market offers now?",
        "Compare the exact same ticket at two different times. The ticket "
        "must contain the same selections, lines, settlement rules, and "
        "boost status for the comparison to be meaningful.",
    )

    st.info(
        "When a ticket moves from a larger positive price to a smaller "
        "positive price—such as +7500 to +6000—the market is treating the "
        "ticket as more likely to win. The original ticket keeps its "
        "better payout."
    )

    comparison_format = st.selectbox(
        "Odds format",
        [
            "American",
            "Decimal",
            "Fractional",
            "Implied probability",
        ],
        key="clv_odds_format",
    )

    try:
        clv_col1, clv_col2 = st.columns(2)

        if comparison_format == "American":
            with clv_col1:
                original_line_input = st.number_input(
                    "Original ticket odds",
                    value=(
                        int(
                            round(
                                st.session_state.parlay_workspace[
                                    "offered_american"
                                ]
                            )
                        )
                        if st.session_state.parlay_workspace
                        else 7500
                    ),
                    step=50,
                    key="clv_original_american",
                )

            with clv_col2:
                current_line_input = st.number_input(
                    "Current odds for the exact same ticket",
                    value=6000,
                    step=50,
                    key="clv_current_american",
                )

        elif comparison_format == "Decimal":
            with clv_col1:
                original_line_input = st.number_input(
                    "Original ticket decimal odds",
                    min_value=1.01,
                    value=76.00,
                    step=0.10,
                    format="%.2f",
                    key="clv_original_decimal",
                )

            with clv_col2:
                current_line_input = st.number_input(
                    "Current exact-ticket decimal odds",
                    min_value=1.01,
                    value=61.00,
                    step=0.10,
                    format="%.2f",
                    key="clv_current_decimal",
                )

        elif comparison_format == "Fractional":
            with clv_col1:
                original_line_input = st.text_input(
                    "Original ticket fractional odds",
                    value="75/1",
                    key="clv_original_fractional",
                )

            with clv_col2:
                current_line_input = st.text_input(
                    "Current exact-ticket fractional odds",
                    value="60/1",
                    key="clv_current_fractional",
                )

        else:
            with clv_col1:
                original_line_input = st.number_input(
                    "Original implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=1.32,
                    step=0.01,
                    format="%.2f",
                    key="clv_original_probability",
                )

            with clv_col2:
                current_line_input = st.number_input(
                    "Current implied probability (%)",
                    min_value=0.01,
                    max_value=99.99,
                    value=1.64,
                    step=0.01,
                    format="%.2f",
                    key="clv_current_probability",
                )

        clv_stake = st.number_input(
            "Original stake ($)",
            min_value=0.01,
            value=(
                float(st.session_state.parlay_workspace["stake"])
                if st.session_state.parlay_workspace
                else 100.00
            ),
            step=10.00,
            format="%.2f",
            key="clv_stake",
        )

        original_line_decimal = convert_input_to_decimal(
            comparison_format,
            original_line_input,
        )
        current_line_decimal = convert_input_to_decimal(
            comparison_format,
            current_line_input,
        )

        clv_results = line_value_metrics(
            original_line_decimal,
            current_line_decimal,
            clv_stake,
        )

        original_american = decimal_to_american(
            original_line_decimal
        )
        current_american = decimal_to_american(
            current_line_decimal
        )

        movement_favorable = (
            original_line_decimal > current_line_decimal
        )
        movement_unfavorable = (
            original_line_decimal < current_line_decimal
        )

        st.divider()
        st.subheader("Price Movement")

        price_col1, price_col2, price_col3 = st.columns(3)

        price_col1.metric(
            "Original price",
            f"{original_american:+.0f}",
        )
        price_col2.metric(
            "Current exact-ticket price",
            f"{current_american:+.0f}",
        )
        price_col3.metric(
            "Profit price advantage",
            f"${clv_results['profit_price_advantage']:+,.2f}",
            help=(
                "How much more or less profit the original ticket pays "
                "than a wager of the same stake placed at the current "
                "price."
            ),
        )

        probability_col1, probability_col2, probability_col3 = (
            st.columns(3)
        )

        probability_col1.metric(
            "Original implied probability",
            f"{clv_results['original_probability']:.2f}%",
        )
        probability_col2.metric(
            "Current implied probability",
            f"{clv_results['current_probability']:.2f}%",
        )
        probability_col3.metric(
            "Market-implied change",
            (
                f"{clv_results['probability_point_change']:+.2f} pts"
            ),
        )

        return_col1, return_col2, return_col3 = st.columns(3)

        return_col1.metric(
            "Original potential profit",
            f"${clv_results['original_profit']:,.2f}",
        )
        return_col2.metric(
            "Profit at current price",
            f"${clv_results['current_profit']:,.2f}",
        )
        return_col3.metric(
            "Relative probability change",
            (
                f"{clv_results['relative_probability_change']:+.2f}%"
            ),
        )

        if movement_favorable:
            st.success(
                "The ticket moved in your favor. You locked in a larger "
                "payout than the market offers now for the exact same "
                "ticket."
            )
        elif movement_unfavorable:
            st.warning(
                "The ticket moved against your entry. The market now "
                "offers a larger payout for the exact same ticket."
            )
        else:
            st.info(
                "The ticket price has not materially changed."
            )

        if movement_favorable:
            takeaway_headline = (
                "You captured positive line value."
            )
            takeaway_meaning = (
                f"You locked in {original_american:+.0f} before the same "
                f"ticket moved to {current_american:+.0f}. On a "
                f"${clv_stake:,.2f} stake, your ticket pays "
                f"${clv_results['profit_price_advantage']:,.2f} more "
                f"profit than the currently available price."
            )
        elif movement_unfavorable:
            takeaway_headline = (
                "The market moved against your entry."
            )
            takeaway_meaning = (
                f"You entered at {original_american:+.0f}, while the same "
                f"ticket is now available at {current_american:+.0f}. A "
                f"${clv_stake:,.2f} wager placed now would pay "
                f"${abs(clv_results['profit_price_advantage']):,.2f} more "
                f"profit."
            )
        else:
            takeaway_headline = (
                "The market price is essentially unchanged."
            )
            takeaway_meaning = (
                "The original and current ticket prices imply nearly the "
                "same payout and probability."
            )

        render_takeaway(
            takeaway_headline,
            takeaway_meaning,
            (
                "Line movement shows how the market repriced the ticket; "
                "it does not prove the original wager was positive EV or "
                "that the ticket will win."
            ),
        )

        with st.expander("What can cause a parlay price to move?"):
            st.markdown(
                """
                - Injury, lineup, or availability news
                - Earlier results changing tournament or playoff paths
                - Movement in one or more individual component markets
                - Changes to same-game correlation adjustments
                - Sportsbook liability or exposure
                - Removal or addition of boosts and promotions
                - Different settlement rules or altered selection lines

                For a valid comparison, the original and current ticket
                must be identical.
                """
            )

        with st.expander("How should an experienced bettor use this?", expanded=advanced_mode):
            st.markdown(
                f"""
                **Original decimal price:** {original_line_decimal:.4f}

                **Current decimal price:** {current_line_decimal:.4f}

                **Original implied probability:**
                {clv_results['original_probability']:.4f}%

                **Current implied probability:**
                {clv_results['current_probability']:.4f}%

                **Probability-point movement:**
                {clv_results['probability_point_change']:+.4f}

                **Relative probability movement:**
                {clv_results['relative_probability_change']:+.2f}%

                Positive line value is generally desirable because the
                original ticket pays more than the current market price.
                For parlays, identifying which event group caused the
                movement requires comparing current component prices.
                """
            )

        st.caption(
            "This compares market prices only. It does not estimate the "
            "ticket's true probability or predict the outcome."
        )

    except ValueError as error:
        st.error(str(error))

# -----------------------------------------------------
# FINAL-LEG HEDGE
# -----------------------------------------------------

with final_leg_tab:
    st.subheader("Final-Leg Parlay Hedge")

    if st.session_state.parlay_workspace:
        st.success("Saved workspace values prefill the original stake and total payout.")


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
                value=(
                    float(st.session_state.parlay_workspace["stake"])
                    if st.session_state.parlay_workspace
                    else 25.00
                ),
                step=5.00,
                format="%.2f",
                key="v08_final_original_stake",
            )

        with final_col2:
            final_total_payout = st.number_input(
                "Total parlay payout if final event wins ($)",
                min_value=0.01,
                value=(
                    float(
                        st.session_state.parlay_workspace[
                            "offered_total_return"
                        ]
                    )
                    if st.session_state.parlay_workspace
                    else 500.00
                ),
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
