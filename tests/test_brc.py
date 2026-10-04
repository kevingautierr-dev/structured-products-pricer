import numpy as np
import pytest

from pricer.analytics import brc_price
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import brc_payoff
from pricer.solver import fair_coupon

S0, R, Q, SIGMA, T = 100.0, 0.03, 0.02, 0.25, 1.0
BARRIER, NOMINAL, MARGIN = 0.60, 100.0, 0.01
TARGET = NOMINAL * (1 - MARGIN)


@pytest.fixture(scope="module")
def terminal_paths():
    return simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=400_000, seed=21)


def test_payoff_scenarios():
    """Hand-checked scenarios: no breach, breach and recovery, breach and loss."""
    paths = np.array([
        [100.0, 90.0, 110.0],   # never below 60 -> 100 + 5
        [100.0, 55.0, 120.0],   # breached, ends above strike -> 100 + 5
        [100.0, 55.0, 50.0],    # breached, ends at 50 -> 50 + 5
    ])
    out = brc_payoff(paths, S0, BARRIER, coupon=0.05, monitoring="continuous")
    assert np.allclose(out, [105.0, 105.0, 55.0])


def test_brc_closed_form_fair_coupon_values():
    """Closed-form fair coupons match the planning values (3.15% and 3.95%)."""
    for monitoring, expected in [("maturity", 0.0315), ("continuous", 0.0395)]:
        c = fair_coupon(lambda c: brc_price(S0, BARRIER, c, R, Q, SIGMA, T, monitoring=monitoring), TARGET)
        assert c == pytest.approx(expected, abs=5e-4)


def test_mc_fair_coupon_matches_closed_form(terminal_paths):
    """MC fair coupon (barrier at maturity) within 3 standard errors of the closed form."""
    def mc(c):
        return mc_price(brc_payoff(terminal_paths, S0, BARRIER, c), R, T)

    c_mc = fair_coupon(lambda c: mc(c)["price"], TARGET)
    c_exact = fair_coupon(lambda c: brc_price(S0, BARRIER, c, R, Q, SIGMA, T), TARGET)
    # one coupon point is worth nominal * e^{-rT} of price, so convert the price error
    coupon_std_err = mc(c_mc)["std_err"] / (NOMINAL * np.exp(-R * T))
    assert abs(c_mc - c_exact) < 3 * coupon_std_err


def test_higher_vol_gives_higher_coupon():
    """The investor sells a put: more volatility -> more expensive put -> higher coupon."""
    coupons = [
        fair_coupon(lambda c, s=s: brc_price(S0, BARRIER, c, R, Q, s, T), TARGET)
        for s in (0.15, 0.25, 0.35)
    ]
    assert coupons[0] < coupons[1] < coupons[2]