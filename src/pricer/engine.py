"""Monte Carlo engine: turns payoffs into a price with its statistical error."""
import numpy as np


def mc_price(payoffs, r, T, antithetic=True):
    """Discounted Monte Carlo price, standard error and 95% confidence interval.

    With antithetic variates, path i and path i + n/2 are mirror images (Z and -Z),
    so they are not independent. The standard error is therefore computed on the
    pair averages, which are independent.

    Returns
    -------
    dict with keys: price, std_err, ci_low, ci_high
    """
    discounted = np.exp(-r * T) * np.asarray(payoffs, dtype=float)
    if antithetic:
        n_half = len(discounted) // 2
        samples = 0.5 * (discounted[:n_half] + discounted[n_half:])
    else:
        samples = discounted
    price = samples.mean()
    std_err = samples.std(ddof=1) / np.sqrt(len(samples))
    return {
        "price": price,
        "std_err": std_err,
        "ci_low": price - 1.96 * std_err,
        "ci_high": price + 1.96 * std_err,
    }