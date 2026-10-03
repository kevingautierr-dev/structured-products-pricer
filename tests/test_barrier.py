import pytest

from pricer.analytics import down_and_in_put_european
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import down_and_in_put_payoff_european

S0, K, H, R, Q, SIGMA, T = 100.0, 100.0, 60.0, 0.03, 0.02, 0.25, 1.0


def test_dip_european_reference_value():
    """Closed form matches the value computed when planning the project."""
    assert down_and_in_put_european(S0, K, H, R, Q, SIGMA, T) == pytest.approx(1.101, abs=1e-3)


def test_dip_european_mc_matches_closed_form():
    """Monte Carlo (one step: only S_T matters) within 3 standard errors."""
    s_T = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=400_000, seed=11)[:, -1]
    result = mc_price(down_and_in_put_payoff_european(s_T, K, H), R, T)
    exact = down_and_in_put_european(S0, K, H, R, Q, SIGMA, T)
    assert abs(result["price"] - exact) < 3 * result["std_err"]