import json

import streamlit as st

from positioniq_calculations import *
from positioniq_components.ui import *


experience_level = get_experience_level()
advanced_mode = is_advanced_mode()

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
