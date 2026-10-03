import numpy as np
import pytest

from pricer.analytics import bs_price
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import call_payoff, put_payoff

S0, K, R, Q, SIGMA, T = 100.0, 100.0, 0.03, 0.02, 0.25, 1.0
N_PATHS = 200_000


@pytest.fixture(scope="module")
def s_T():
    """Terminal prices: one step is enough for European options (exact GBM scheme)."""
    paths = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=N_PATHS, seed=42)
    return paths[:, -1]


def test_bs_put_call_parity():
    """C - P = S0 e^{-qT} - K e^{-rT} must hold exactly for the closed forms."""
    call = bs_price(S0, K, R, Q, SIGMA, T, "call")
    put = bs_price(S0, K, R, Q, SIGMA, T, "put")
    assert call - put == pytest.approx(S0 * np.exp(-Q * T) - K * np.exp(-R * T))


def test_bs_put_reference_value():
    """Regression check against the value computed when planning the project."""
    assert bs_price(S0, K, R, Q, SIGMA, T, "put") == pytest.approx(9.222, abs=1e-3)


@pytest.mark.parametrize("option, payoff", [("call", call_payoff), ("put", put_payoff)])
def test_mc_matches_black_scholes(s_T, option, payoff):
    """Monte Carlo price within 3 standard errors of Black-Scholes."""
    result = mc_price(payoff(s_T, K), R, T)
    exact = bs_price(S0, K, R, Q, SIGMA, T, option)
    assert abs(result["price"] - exact) < 3 * result["std_err"]