import numpy as np
import pytest

from pricer.engine import mc_estimate
from pricer.paths import simulate_gbm
from pricer.products import phoenix_pv
from pricer.solver import fair_coupon

S0, R, Q, SIGMA = 100.0, 0.03, 0.02, 0.25
T, N_OBS = 3.0, 12
TIMES = np.linspace(T / N_OBS, T, N_OBS)
TARGET = 99.0


def test_memory_hand_example():
    """Coupons missed at dates 1-2 are paid at date 3 (memory), then autocall at date 4."""
    perf = np.array([[0.65, 0.68, 0.80, 1.05]])
    times = np.array([1.0, 2.0, 3.0, 4.0])
    pv = phoenix_pv(perf, times, r=0.0, coupon=0.02)
    # date 3: 3 coupons of 2 = 6 ; date 4: coupon 2 + nominal 100 -> total 108
    assert pv[0] == pytest.approx(108.0)
    pv_no_mem = phoenix_pv(perf, times, r=0.0, coupon=0.02, memory=False)
    assert pv_no_mem[0] == pytest.approx(104.0)


def test_loss_at_maturity_below_protection():
    """Never called, below 60% at the end: investor gets nominal * final performance."""
    perf = np.array([[0.9, 0.5]])
    pv = phoenix_pv(perf, np.array([1.0, 2.0]), r=0.0, coupon=0.02)
    assert pv[0] == pytest.approx(2.0 + 50.0)  # coupon at date 1 only, redemption 50


def test_zero_vol_autocalls_at_first_date():
    """No volatility, r > q: performance > 100% at date 1 -> immediate autocall."""
    paths = simulate_gbm(S0, R, Q, 1e-8, T, N_OBS, n_paths=10, seed=0)
    pv = phoenix_pv(paths[:, 1:] / S0, TIMES, R, coupon=0.02)
    assert np.allclose(pv, np.exp(-R * TIMES[0]) * 100.0 * 1.02)


def test_all_coupons_paid_when_barriers_trivial():
    """Coupon barrier 0, no autocall, no loss: a plain coupon bond, priced in closed form."""
    paths = simulate_gbm(S0, R, Q, SIGMA, T, N_OBS, n_paths=1000, seed=0)
    pv = phoenix_pv(paths[:, 1:] / S0, TIMES, R, coupon=0.02, coupon_barrier=0.0,
                    autocall_barrier=np.inf, protection_barrier=0.0)
    bond = 100.0 * 0.02 * np.exp(-R * TIMES).sum() + 100.0 * np.exp(-R * T)
    assert np.allclose(pv, bond)


def test_memory_coupon_is_lower():
    """Memory makes each coupon more valuable, so the fair coupon is lower."""
    perf = simulate_gbm(S0, R, Q, SIGMA, T, N_OBS, n_paths=100_000, seed=3)[:, 1:] / S0
    c_mem = fair_coupon(lambda c: mc_estimate(phoenix_pv(perf, TIMES, R, c))["price"], TARGET)
    c_nomem = fair_coupon(lambda c: mc_estimate(phoenix_pv(perf, TIMES, R, c, memory=False))["price"], TARGET)
    assert c_mem < c_nomem