import numpy as np
import pytest

from pricer.analytics import bs_greeks
from pricer.engine import mc_price
from pricer.greeks import bump_greeks
from pricer.paths import simulate_gbm
from pricer.products import call_payoff

K, Q, T, SEED, N = 100.0, 0.02, 1.0, 42, 400_000


def call_price(s0, sigma, r):
    """Same seed on every call: common random numbers across bumps."""
    s_T = simulate_gbm(s0, r, Q, sigma, T, n_steps=1, n_paths=N, seed=SEED)[:, -1]
    return mc_price(call_payoff(s_T, K), r, T)["price"]


@pytest.fixture(scope="module")
def greeks():
    return bump_greeks(call_price, 100.0, 0.25, 0.03), bs_greeks(100.0, K, 0.03, Q, 0.25, T)


@pytest.mark.parametrize("name, tol", [("delta", 0.005), ("vega", 0.005), ("rho", 0.0005), ("gamma", 0.002)])
def test_call_greeks_match_black_scholes(greeks, name, tol):
    mc, bs = greeks
    assert mc[name] == pytest.approx(bs[name], abs=tol)


def test_common_random_numbers_reduce_noise():
    """Delta with a new seed in the bumped scenario is far noisier than with the same seed."""
    def delta(same_seed, seed):
        up = simulate_gbm(101.0, 0.03, Q, 0.25, T, 1, 20_000, seed=seed)[:, -1]
        dn = simulate_gbm(99.0, 0.03, Q, 0.25, T, 1, 20_000, seed=seed if same_seed else seed + 1000)[:, -1]
        return (call_payoff(up, K).mean() - call_payoff(dn, K).mean()) / 2.0

    crn = np.std([delta(True, s) for s in range(30)])
    indep = np.std([delta(False, s) for s in range(30)])
    assert crn < indep / 10