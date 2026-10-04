"""Greeks by bump-and-revalue (finite differences) with common random numbers.

The price function must re-simulate with the SAME seed for every bumped input.
The random draws are then identical in the base and bumped scenarios, so the
difference of two prices reflects the bump, not Monte Carlo noise.
"""


def bump_greeks(price_fn, s0, sigma, r, rel_spot_bump=0.01, vol_bump=0.01, rate_bump=0.0001):
    """Delta, gamma, vega, rho of price_fn(s0, sigma, r) by central differences.

    Returns
    -------
    dict with:
      delta : dPrice / dSpot
      gamma : d2Price / dSpot2
      vega  : price change for +1 vol point (sigma + 0.01)
      rho   : price change for +1 basis point of rate (r + 0.0001)
    """
    h = s0 * rel_spot_bump
    p0 = price_fn(s0, sigma, r)
    p_up, p_dn = price_fn(s0 + h, sigma, r), price_fn(s0 - h, sigma, r)
    v_up, v_dn = price_fn(s0, sigma + vol_bump, r), price_fn(s0, sigma - vol_bump, r)
    r_up, r_dn = price_fn(s0, sigma, r + rate_bump), price_fn(s0, sigma, r - rate_bump)
    return {
        "price": p0,
        "delta": (p_up - p_dn) / (2 * h),
        "gamma": (p_up - 2 * p0 + p_dn) / h**2,
        "vega": (v_up - v_dn) / (2 * vol_bump) * 0.01,
        "rho": (r_up - r_dn) / (2 * rate_bump) * 0.0001,
    }