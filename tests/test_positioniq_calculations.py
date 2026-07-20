import math

from positioniq_calculations import (
    american_to_decimal,
    cashout_break_even_probability,
    combine_decimal_odds,
    combine_independent_probabilities,
    decimal_to_probability,
    expected_value,
    full_hedge_amount,
    line_value_metrics,
    remove_vig_two_way,
)


def test_american_to_decimal_positive():
    assert math.isclose(american_to_decimal(150), 2.5)


def test_american_to_decimal_negative():
    assert math.isclose(american_to_decimal(-110), 1.9090909091)


def test_two_way_no_vig_totals_100():
    fair_a, fair_b, _ = remove_vig_two_way(
        american_to_decimal(-120),
        american_to_decimal(105),
    )
    assert math.isclose(fair_a + fair_b, 100.0, abs_tol=1e-9)


def test_expected_value_positive():
    assert math.isclose(expected_value(100, 2.5, 45), 12.5)


def test_equal_profit_hedge():
    hedge = full_hedge_amount(100, 2.2, american_to_decimal(-110))
    assert math.isclose(hedge, 115.2380952381)


def test_cashout_break_even_probability():
    assert math.isclose(
        cashout_break_even_probability(180, 300),
        60.0,
    )


def test_independent_parlay_probability():
    combined = combine_independent_probabilities([60, 60, 60])
    assert math.isclose(combined, 21.6)


def test_combined_decimal_odds():
    combined = combine_decimal_odds([4.0, 3.0, 1.9090909091])
    assert math.isclose(combined, 22.9090909092)


def test_line_value_favorable():
    metrics = line_value_metrics(76.0, 61.0, 100)
    assert metrics["profit_price_advantage"] == 1500
    assert metrics["probability_point_change"] > 0


def test_decimal_probability():
    assert math.isclose(decimal_to_probability(2.5), 40.0)
