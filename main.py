#!/usr/bin/env python
import argparse

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tool to calculate how screwed you're getting on a parlay"
    )
    parser.add_argument(
        "leg_odds", nargs="+", type=float, help="List of American odds in parlay"
    )
    parser.add_argument(
        "--total-odds", type=float, help="American odds offered for total parlay"
    )
    parser.add_argument(
        "--take", type=float, default=0.1, help="Casino take as a fracion"
    )

    args = parser.parse_args()

    # American odds for each leg
    leg_odds: list[float] = args.leg_odds
    total_odds: float = (
        total_parlay_odds(leg_odds) if args.total_odds is None else args.total_odds
    )
    print(round(total_odds), "total odds")

    # The fraction of winnings the bettor gets to keep
    gamma: float = 1.0 - args.take
    leg_probs = ([1.0 / (1.0 + winnings_from_amer(odds) / gamma) for odds in leg_odds],)

    implied_parlay_prob: float = np.prod(leg_probs, dtype=float)

    # print(implied_parlay_prob, "implied probability")
    # "fair" in the sense that the casino's take is the same
    fair_payout: float = 1.0 + gamma * (1.0 / implied_parlay_prob - 1)
    fair_odds: float = amer_from_payout(fair_payout)
    print(round(fair_odds), "fair odds")


def winnings_from_amer(amer: float) -> float:
    """
    Return the total payout if the bet is won for the given american line.

    This is the reciprocal of the implied probability of the event (with no casino take).
    """
    if amer >= 100.0:
        return amer / 100.0
    if amer <= -100.0:
        return -100.0 / amer
    raise ValueError(f"{amer} inside (-100, 100)")


def payout_from_amer(amer: float) -> float:
    """
    Decimal odds from American. This is the total payout ratio in the event of a win.
    """
    return 1.0 + winnings_from_amer(amer)


def amer_from_payout(payout: float) -> float:
    """
    Return the american odds given the payout.
    """
    winnings = payout - 1.0
    if winnings >= 1.0:
        return 100.0 * winnings
    else:
        return -100.0 / winnings


def total_parlay_odds(leg_odds: list[float]) -> float:
    """
    Return the odds that should be offered for the list of American odds
    """
    payouts: list[float] = [payout_from_amer(odds) for odds in leg_odds]
    combined_payout: float = np.prod(payouts, dtype=float)
    return amer_from_payout(combined_payout)


if __name__ == "__main__":
    main()
