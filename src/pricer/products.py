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


def phoenix_pv(perf, obs_times, r, coupon, coupon_barrier=0.70, autocall_barrier=1.00,
               protection_barrier=0.60, nominal=100.0, memory=True):
    """Present value, path by path, of a Phoenix autocall with memory coupon.

    Parameters
    ----------
    perf : array (n_paths, n_obs)  Performance S(t_i)/S0 at each observation date.
                                   For a worst-of, pass the minimum performance across assets.
    obs_times : array (n_obs,)     Observation dates in years (e.g. 0.25, 0.5, ..., 3.0).
    coupon : float                 Coupon per observation period, as a fraction of nominal.
    memory : bool                  If True, missed coupons are paid later when the barrier is met.

    At each date t_i, for paths still alive:
      1. coupon test: perf >= coupon_barrier -> pay coupon * (1 + missed coupons)
      2. autocall test (all dates but the last): perf >= autocall_barrier -> repay nominal, stop
      3. last date: repay nominal if perf >= protection_barrier, else nominal * perf
    Each cash flow is discounted from its own payment date.
    """
    n_paths, n_obs = perf.shape
    pv = np.zeros(n_paths)
    alive = np.ones(n_paths, dtype=bool)
    missed = np.zeros(n_paths)

    for i in range(n_obs):
        p = perf[:, i]
        df = np.exp(-r * obs_times[i])

        coupon_paid = alive & (p >= coupon_barrier)
        n_coupons = (missed + 1) if memory else 1.0
        pv += df * nominal * coupon * n_coupons * coupon_paid
        missed = np.where(coupon_paid, 0.0, missed + alive)

        if i < n_obs - 1:
            called = alive & (p >= autocall_barrier)
            pv += df * nominal * called
            alive &= ~called
        else:
            redemption = np.where(p >= protection_barrier, nominal, nominal * p)
            pv += df * redemption * alive
    return pv