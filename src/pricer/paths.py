"""Path simulation under risk-neutral geometric Brownian motion (GBM)."""
import numpy as np


def simulate_gbm(s0, r, q, sigma, T, n_steps, n_paths, seed=None, antithetic=True):
    """Simulate GBM price paths under the risk-neutral measure.

    Exact log-normal scheme (no discretisation error at the grid dates):
        S(t+dt) = S(t) * exp((r - q - 0.5*sigma**2)*dt + sigma*sqrt(dt)*Z)

    Parameters
    ----------
    s0 : float        Spot price today.
    r : float         Risk-free rate (continuous, annual).
    q : float         Dividend yield (continuous, annual).
    sigma : float     Volatility (annual).
    T : float         Maturity in years.
    n_steps : int     Number of time steps; dt = T / n_steps.
    n_paths : int     Number of paths (must be even if antithetic).
    seed : int        Random seed, for reproducible results.
    antithetic : bool If True, each draw Z is paired with -Z (variance reduction).

    Returns
    -------
    np.ndarray, shape (n_paths, n_steps + 1). Column 0 is s0, last column is S_T.
    """
    if antithetic and n_paths % 2 != 0:
        raise ValueError("n_paths must be even when antithetic=True")

    rng = np.random.default_rng(seed)
    dt = T / n_steps

    # Random shocks Z ~ N(0,1): one row per path, one column per step
    if antithetic:
        half = rng.standard_normal((n_paths // 2, n_steps))
        z = np.concatenate([half, -half], axis=0)
    else:
        z = rng.standard_normal((n_paths, n_steps))

    # Log-return of each step: trend + convexity correction + random shock
    log_increments = (r - q - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z

    # Cumulative sum = log-return from today to each date, for all paths at once
    log_paths = np.cumsum(log_increments, axis=1)

    paths = s0 * np.exp(log_paths)
    first_column = np.full((n_paths, 1), s0)
    return np.hstack([first_column, paths])