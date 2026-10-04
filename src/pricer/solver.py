"""Fair coupon solver: find the coupon that makes the product worth 100% minus the issuer margin."""
from scipy.optimize import brentq


def fair_coupon(price_fn, target, low=0.0, high=1.0):
    """Coupon c such that price_fn(c) == target.

    price_fn must be increasing in c and evaluated on fixed random numbers
    (same paths for every c), so that it is a smooth deterministic function.
    """
    return brentq(lambda c: price_fn(c) - target, low, high, xtol=1e-10)