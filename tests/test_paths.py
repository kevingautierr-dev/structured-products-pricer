import numpy as np
from pricer.paths import simulate_gbm

S0, R, Q, SIGMA, T = 100.0, 0.03, 0.02, 0.25, 1.0


def test_shape_and_start():
    """One row per path, one column per date, first column equal to S0."""
    paths = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=12, n_paths=1000, seed=1)
    assert paths.shape == (1000, 13)
    assert np.all(paths[:, 0] == S0)


def test_zero_vol_gives_forward():
    """With sigma = 0 the path is deterministic: S_T = S0 * exp((r - q) * T)."""
    paths = simulate_gbm(S0, R, Q, 0.0, T, n_steps=4, n_paths=10, seed=1)
    assert np.allclose(paths[:, -1], S0 * np.exp((R - Q) * T))


def test_terminal_mean_matches_forward():
    """Risk-neutral mean of S_T equals the forward, within 3 standard errors."""
    paths = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=200_000, seed=7)
    s_T = paths[:, -1]
    forward = S0 * np.exp((R - Q) * T)
    std_err = s_T.std(ddof=1) / np.sqrt(len(s_T))
    assert abs(s_T.mean() - forward) < 3 * std_err