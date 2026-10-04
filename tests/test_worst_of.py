import numpy as np
import pytest

from pricer.engine import mc_estimate
from pricer.paths import constant_corr_matrix, simulate_gbm_multi
from pricer.products import phoenix_pv
from pricer.solver import fair_coupon

R = 0.03
S0 = np.array([100.0, 50.0, 200.0])
Q = np.array([0.02, 0.01, 0.03])
SIGMA = np.array([0.25, 0.20, 0.30])
T, N_OBS = 3.0, 12
TIMES = np.linspace(T / N_OBS, T, N_OBS)


def test_shape_and_start():
    paths = simulate_gbm_multi(S0, R, Q, SIGMA, constant_corr_matrix(3, 0.5), 1.0, 4, 100, seed=1)
    assert paths.shape == (100, 5, 3)
    assert np.allclose(paths[:, 0, :], S0)


def test_empirical_correlation_matches_target():
    """Correlation of simulated log-returns equals the input matrix (Cholesky check)."""
    corr = np.array([[1.0, 0.6, 0.2], [0.6, 1.0, -0.3], [0.2, -0.3, 1.0]])
    paths = simulate_gbm_multi(S0, R, Q, SIGMA, corr, 1.0, 1, 400_000, seed=2)
    log_ret = np.log(paths[:, 1, :] / paths[:, 0, :])
    assert np.allclose(np.corrcoef(log_ret.T), corr, atol=0.01)


def test_each_asset_matches_its_forward():
    """Marginal risk-neutral mean of each asset equals its own forward."""
    paths = simulate_gbm_multi(S0, R, Q, SIGMA, constant_corr_matrix(3, 0.5), 1.0, 1, 400_000, seed=3)
    forward = S0 * np.exp((R - Q) * 1.0)
    assert np.allclose(paths[:, -1, :].mean(axis=0), forward, rtol=3e-3)


def test_worst_of_coupon_falls_with_correlation():
    """Investor is short correlation: the higher rho, the lower the fair coupon."""
    coupons = []
    for rho in (0.2, 0.5, 0.8):
        paths = simulate_gbm_multi(S0, R, Q, SIGMA, constant_corr_matrix(3, rho), T, N_OBS, 60_000, seed=4)
        worst = (paths[:, 1:, :] / S0).min(axis=2)
        coupons.append(fair_coupon(lambda c: mc_estimate(phoenix_pv(worst, TIMES, R, c))["price"], 99.0))
    assert coupons[0] > coupons[1] > coupons[2]