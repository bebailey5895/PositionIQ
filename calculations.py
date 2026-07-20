from fractions import Fraction


def validate_decimal(decimal_odds: float) -> None:
    """Ensure decimal odds are valid."""
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1.00.")


def american_to_decimal(american_odds: float) -> float:
    """Convert American odds to decimal odds."""
    if american_odds == 0:
        raise ValueError("American odds cannot be 0.")

    if -100 < american_odds < 100:
        raise ValueError(
            "American odds must normally be +100 or greater, "
            "or -100 or lower."
        )

    if american_odds > 0:
        return 1 + american_odds / 100

    return 1 + 100 / abs(american_odds)


def decimal_to_american(decimal_odds: float) -> float:
    """Convert decimal odds to American odds."""
    validate_decimal(decimal_odds)

    if decimal_odds >= 2:
        return (decimal_odds - 1) * 100

    return -100 / (decimal_odds - 1)


def fractional_to_decimal(fractional_odds: str) -> float:
    """Convert fractional odds such as 6/5 into decimal odds."""
    try:
        fraction = Fraction(fractional_odds.strip())
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(
            "Enter fractional odds in a format such as 6/5 or 5/2."
        ) from exc

    if fraction <= 0:
        raise ValueError("Fractional odds must be greater than 0.")

    return 1 + float(fraction)


def decimal_to_fractional(
    decimal_odds: float,
    max_denominator: int = 100,
) -> str:
    """Convert decimal odds into simplified fractional odds."""
    validate_decimal(decimal_odds)

    fraction = Fraction(
        decimal_odds - 1
    ).limit_denominator(max_denominator)

    return f"{fraction.numerator}/{fraction.denominator}"


def probability_to_decimal(probability_percent: float) -> float:
    """Convert implied probability percentage into decimal odds."""
    if probability_percent <= 0 or probability_percent >= 100:
        raise ValueError(
            "Probability must be greater than 0% and less than 100%."
        )

    return 100 / probability_percent


def decimal_to_probability(decimal_odds: float) -> float:
    """Convert decimal odds into implied probability percentage."""
    validate_decimal(decimal_odds)
    return 100 / decimal_odds


def calculate_profit(
    stake: float,
    decimal_odds: float,
) -> float:
    """Calculate net profit, excluding the returned stake."""
    if stake < 0:
        raise ValueError("Stake cannot be negative.")

    validate_decimal(decimal_odds)
    return stake * (decimal_odds - 1)


def calculate_total_return(
    stake: float,
    decimal_odds: float,
) -> float:
    """Calculate total return, including the original stake."""
    if stake < 0:
        raise ValueError("Stake cannot be negative.")

    validate_decimal(decimal_odds)
    return stake * decimal_odds


def remove_vig_two_way(
    decimal_odds_a: float,
    decimal_odds_b: float,
) -> tuple[float, float, float]:
    """
    Remove vig proportionally from a two-outcome market.

    Returns:
        fair_probability_a
        fair_probability_b
        market_margin

    All returned values are percentages.
    """
    validate_decimal(decimal_odds_a)
    validate_decimal(decimal_odds_b)

    raw_probability_a = 1 / decimal_odds_a
    raw_probability_b = 1 / decimal_odds_b

    combined_probability = raw_probability_a + raw_probability_b

    fair_probability_a = (
        raw_probability_a / combined_probability
    ) * 100

    fair_probability_b = (
        raw_probability_b / combined_probability
    ) * 100

    market_margin = (combined_probability - 1) * 100

    return (
        fair_probability_a,
        fair_probability_b,
        market_margin,
    )