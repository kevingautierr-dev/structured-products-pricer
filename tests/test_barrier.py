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
    

from pricer.analytics import bgk_shift, down_and_in_put_continuous
from pricer.products import down_and_in_put_payoff_continuous

N_DAILY = 252


def test_dip_continuous_reference_value():
    """Reiner-Rubinstein closed form matches the planning value."""
    assert down_and_in_put_continuous(S0, K, H, R, Q, SIGMA, T) == pytest.approx(1.882, abs=1e-3)


def test_continuous_worth_more_than_maturity_only():
    """Checking the barrier more often can only activate the put more often."""
    assert down_and_in_put_continuous(S0, K, H, R, Q, SIGMA, T) > down_and_in_put_european(
        S0, K, H, R, Q, SIGMA, T
    )


@pytest.fixture(scope="module")
def daily_paths():
    return simulate_gbm(S0, R, Q, SIGMA, T, n_steps=N_DAILY, n_paths=60_000, seed=5)


def test_daily_monitoring_underprices_continuous(daily_paths):
    """Without correction, daily checks miss crossings: price biased low."""
    result = mc_price(down_and_in_put_payoff_continuous(daily_paths, K, H), R, T)
    exact = down_and_in_put_continuous(S0, K, H, R, Q, SIGMA, T)
    assert result["price"] < exact


def test_bgk_corrected_matches_continuous(daily_paths):
    """With the BGK-shifted barrier, MC matches the continuous closed form."""
    h_adj = bgk_shift(H, SIGMA, T / N_DAILY)
    result = mc_price(down_and_in_put_payoff_continuous(daily_paths, K, h_adj), R, T)
    exact = down_and_in_put_continuous(S0, K, H, R, Q, SIGMA, T)
    assert abs(result["price"] - exact) < 3 * result["std_err"]