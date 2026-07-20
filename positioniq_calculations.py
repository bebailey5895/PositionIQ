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
    """Remove vig proportionally from a two-outcome market."""
    validate_decimal(decimal_odds_a)
    validate_decimal(decimal_odds_b)

    raw_a = 1 / decimal_odds_a
    raw_b = 1 / decimal_odds_b
    combined = raw_a + raw_b

    fair_a = raw_a / combined * 100
    fair_b = raw_b / combined * 100
    overround = (combined - 1) * 100

    return fair_a, fair_b, overround


def remove_vig_three_way(
    decimal_odds_a: float,
    decimal_odds_draw: float,
    decimal_odds_b: float,
) -> tuple[float, float, float, float]:
    """Remove vig proportionally from a three-outcome market."""
    validate_decimal(decimal_odds_a)
    validate_decimal(decimal_odds_draw)
    validate_decimal(decimal_odds_b)

    raw_a = 1 / decimal_odds_a
    raw_draw = 1 / decimal_odds_draw
    raw_b = 1 / decimal_odds_b
    combined = raw_a + raw_draw + raw_b

    fair_a = raw_a / combined * 100
    fair_draw = raw_draw / combined * 100
    fair_b = raw_b / combined * 100
    overround = (combined - 1) * 100

    return fair_a, fair_draw, fair_b, overround


def full_hedge_amount(
    original_stake: float,
    original_decimal_odds: float,
    hedge_decimal_odds: float,
) -> float:
    """Calculate the hedge stake that equalizes profit across two outcomes."""
    if original_stake <= 0:
        raise ValueError("Original stake must be greater than 0.")

    validate_decimal(original_decimal_odds)
    validate_decimal(hedge_decimal_odds)

    original_total_return = original_stake * original_decimal_odds
    return original_total_return / hedge_decimal_odds


def stake_protection_hedge_amount(
    original_stake: float,
    hedge_decimal_odds: float,
) -> float:
    """Calculate the hedge stake that recovers the original stake."""
    if original_stake <= 0:
        raise ValueError("Original stake must be greater than 0.")

    validate_decimal(hedge_decimal_odds)
    return original_stake / (hedge_decimal_odds - 1)


def hedge_outcome_profits(
    original_stake: float,
    original_decimal_odds: float,
    hedge_stake: float,
    hedge_decimal_odds: float,
) -> tuple[float, float]:
    """Calculate net profit under either exclusive outcome."""
    if original_stake <= 0:
        raise ValueError("Original stake must be greater than 0.")

    if hedge_stake < 0:
        raise ValueError("Hedge stake cannot be negative.")

    validate_decimal(original_decimal_odds)
    validate_decimal(hedge_decimal_odds)

    original_profit = (
        original_stake * original_decimal_odds
        - original_stake
        - hedge_stake
    )

    hedge_profit = (
        hedge_stake * hedge_decimal_odds
        - hedge_stake
        - original_stake
    )

    return original_profit, hedge_profit


def expected_value(
    stake: float,
    decimal_odds: float,
    estimated_probability_percent: float,
) -> float:
    """
    Calculate expected profit or loss per wager in currency units.

    EV = p(win) * net_win - p(loss) * stake
    """
    if stake <= 0:
        raise ValueError("Stake must be greater than 0.")

    validate_decimal(decimal_odds)

    if (
        estimated_probability_percent <= 0
        or estimated_probability_percent >= 100
    ):
        raise ValueError(
            "Estimated probability must be greater than 0% "
            "and less than 100%."
        )

    win_probability = estimated_probability_percent / 100
    loss_probability = 1 - win_probability
    net_win = stake * (decimal_odds - 1)

    return (
        win_probability * net_win
        - loss_probability * stake
    )


def expected_value_percent(
    decimal_odds: float,
    estimated_probability_percent: float,
) -> float:
    """Calculate expected value as a percentage of stake."""
    validate_decimal(decimal_odds)

    if (
        estimated_probability_percent <= 0
        or estimated_probability_percent >= 100
    ):
        raise ValueError(
            "Estimated probability must be greater than 0% "
            "and less than 100%."
        )

    probability = estimated_probability_percent / 100
    return ((probability * decimal_odds) - 1) * 100


def probability_edge(
    decimal_odds: float,
    estimated_probability_percent: float,
) -> float:
    """Return estimated probability minus sportsbook implied probability."""
    implied_probability = decimal_to_probability(decimal_odds)
    return estimated_probability_percent - implied_probability


def break_even_probability(decimal_odds: float) -> float:
    """Return the win rate required to break even at the listed odds."""
    return decimal_to_probability(decimal_odds)

def fair_cashout_value(
    total_payout: float,
    current_win_probability_percent: float,
) -> float:
    """
    Estimate the current fair value of an unsettled ticket.

    Fair ticket value = probability of winning * total payout.
    """
    if total_payout <= 0:
        raise ValueError("Total payout must be greater than 0.")

    if (
        current_win_probability_percent <= 0
        or current_win_probability_percent >= 100
    ):
        raise ValueError(
            "Current win probability must be greater than 0% "
            "and less than 100%."
        )

    probability = current_win_probability_percent / 100
    return total_payout * probability


def cashout_break_even_probability(
    cashout_offer: float,
    total_payout: float,
) -> float:
    """
    Return the win probability at which cashing out and continuing
    have the same expected value.
    """
    if cashout_offer < 0:
        raise ValueError("Cashout offer cannot be negative.")

    if total_payout <= 0:
        raise ValueError("Total payout must be greater than 0.")

    return cashout_offer / total_payout * 100


def cashout_value_difference(
    cashout_offer: float,
    fair_value: float,
) -> float:
    """
    Return cashout offer minus estimated fair ticket value.

    Positive values indicate an offer above estimated fair value.
    Negative values indicate a discount below estimated fair value.
    """
    if cashout_offer < 0:
        raise ValueError("Cashout offer cannot be negative.")

    if fair_value < 0:
        raise ValueError("Fair value cannot be negative.")

    return cashout_offer - fair_value


def cashout_offer_percentage(
    cashout_offer: float,
    fair_value: float,
) -> float:
    """Return the cashout offer as a percentage of estimated fair value."""
    if cashout_offer < 0:
        raise ValueError("Cashout offer cannot be negative.")

    if fair_value <= 0:
        raise ValueError("Fair value must be greater than 0.")

    return cashout_offer / fair_value * 100

def combine_independent_probabilities(
    probabilities_percent: list[float],
) -> float:
    """
    Combine independent leg probabilities into one parlay probability.

    Each input is a percentage between 0 and 100.
    """
    if not probabilities_percent:
        raise ValueError("Enter at least one probability.")

    combined = 1.0

    for probability_percent in probabilities_percent:
        if probability_percent <= 0 or probability_percent >= 100:
            raise ValueError(
                "Every leg probability must be greater than 0% "
                "and less than 100%."
            )

        combined *= probability_percent / 100

    return combined * 100


def combine_decimal_odds(
    decimal_odds_values: list[float],
) -> float:
    """Multiply decimal odds for independent parlay legs."""
    if not decimal_odds_values:
        raise ValueError("Enter at least one set of odds.")

    combined = 1.0

    for decimal_odds in decimal_odds_values:
        validate_decimal(decimal_odds)
        combined *= decimal_odds

    return combined


def fair_decimal_odds_from_probability(
    probability_percent: float,
) -> float:
    """Return fair decimal odds for a probability estimate."""
    return probability_to_decimal(probability_percent)


def parlay_final_leg_equal_profit_hedge(
    total_ticket_payout: float,
    hedge_decimal_odds: float,
) -> float:
    """
    Calculate the opposing hedge needed to equalize profit when exactly
    one two-way parlay leg remains.
    """
    if total_ticket_payout <= 0:
        raise ValueError("Total ticket payout must be greater than 0.")

    validate_decimal(hedge_decimal_odds)
    return total_ticket_payout / hedge_decimal_odds


def parlay_final_leg_outcomes(
    original_stake: float,
    total_ticket_payout: float,
    hedge_stake: float,
    hedge_decimal_odds: float,
) -> tuple[float, float]:
    """
    Return net profits if the parlay wins or the opposing hedge wins.
    """
    if original_stake <= 0:
        raise ValueError("Original stake must be greater than 0.")

    if total_ticket_payout <= 0:
        raise ValueError("Total ticket payout must be greater than 0.")

    if hedge_stake < 0:
        raise ValueError("Hedge stake cannot be negative.")

    validate_decimal(hedge_decimal_odds)

    parlay_win_profit = total_ticket_payout - original_stake - hedge_stake
    hedge_win_profit = (
        hedge_stake * hedge_decimal_odds
        - hedge_stake
        - original_stake
    )

    return parlay_win_profit, hedge_win_profit

def relative_price_difference_percent(
    offered_decimal_odds: float,
    reference_decimal_odds: float,
) -> float:
    """
    Compare an offered decimal price with a reference decimal price.

    Positive values mean the offered price pays more than the reference.
    """
    validate_decimal(offered_decimal_odds)
    validate_decimal(reference_decimal_odds)

    return (
        (offered_decimal_odds - reference_decimal_odds)
        / reference_decimal_odds
        * 100
    )

def line_value_metrics(
    original_decimal_odds: float,
    current_decimal_odds: float,
    stake: float,
) -> dict[str, float]:
    """
    Compare an original ticket price with the current price for the exact
    same ticket.

    Positive price advantage means the bettor locked in a better payout than
    the currently available market.
    """
    validate_decimal(original_decimal_odds)
    validate_decimal(current_decimal_odds)

    if stake <= 0:
        raise ValueError("Stake must be greater than 0.")

    original_probability = decimal_to_probability(
        original_decimal_odds
    )
    current_probability = decimal_to_probability(
        current_decimal_odds
    )

    probability_point_change = (
        current_probability - original_probability
    )

    relative_probability_change = (
        probability_point_change / original_probability * 100
    )

    original_total_return = calculate_total_return(
        stake,
        original_decimal_odds,
    )
    current_total_return = calculate_total_return(
        stake,
        current_decimal_odds,
    )

    original_profit = calculate_profit(
        stake,
        original_decimal_odds,
    )
    current_profit = calculate_profit(
        stake,
        current_decimal_odds,
    )

    return {
        "original_probability": original_probability,
        "current_probability": current_probability,
        "probability_point_change": probability_point_change,
        "relative_probability_change": relative_probability_change,
        "original_total_return": original_total_return,
        "current_total_return": current_total_return,
        "original_profit": original_profit,
        "current_profit": current_profit,
        "profit_price_advantage": original_profit - current_profit,
        "total_return_advantage": (
            original_total_return - current_total_return
        ),
        "decimal_price_advantage": (
            original_decimal_odds - current_decimal_odds
        ),
    }

