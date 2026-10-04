"""Payoff functions. Each takes simulated prices and returns one payoff per path."""
import numpy as np


def call_payoff(s_T, K):
    """European call payoff: max(S_T - K, 0) for each path."""
    return np.maximum(s_T - K, 0.0)


def put_payoff(s_T, K):
    """European put payoff: max(K - S_T, 0) for each path."""
    return np.maximum(K - s_T, 0.0)


def down_and_in_put_payoff_european(s_T, K, H):
    """Down-and-in put, barrier observed at maturity only.
    Pays K - S_T if S_T < H, else 0."""
    return np.where(s_T < H, K - s_T, 0.0)


def down_and_in_put_payoff_continuous(paths, K, H):
    """Down-and-in put, barrier monitored along the whole path.
    Pays max(K - S_T, 0) if the path ever touched H, else 0."""
    s_T = paths[:, -1]
    hit = paths.min(axis=1) <= H
    return np.where(hit, np.maximum(K - s_T, 0.0), 0.0)


def brc_payoff(paths, s0, barrier, coupon, nominal=100.0, monitoring="maturity"):
    """Barrier Reverse Convertible payoff at maturity (single coupon paid at T).

    Parameters
    ----------
    paths : array (n_paths, n_steps + 1). Only the last column is used if monitoring="maturity".
    s0 : float          Initial level of the underlying (strike = 100% of s0).
    barrier : float     Knock-in barrier as a fraction of s0 (e.g. 0.60).
    coupon : float      Coupon as a fraction of nominal (e.g. 0.05), paid in all scenarios.
    monitoring : str    "maturity" (barrier checked on S_T only) or "continuous" (whole path).

    Redemption: nominal if the barrier was never breached, otherwise
    nominal * min(S_T / s0, 1) (the investor bears the loss of the underlying).
    """
    perf = paths[:, -1] / s0
    if monitoring == "maturity":
        knocked_in = perf < barrier
    elif monitoring == "continuous":
        knocked_in = paths.min(axis=1) / s0 <= barrier
    else:
        raise ValueError("monitoring must be 'maturity' or 'continuous'")
    redemption = np.where(knocked_in, nominal * np.minimum(perf, 1.0), nominal)
    return redemption + nominal * coupon