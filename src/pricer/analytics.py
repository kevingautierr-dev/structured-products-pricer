"""Closed-form prices used to validate the Monte Carlo engine."""
import numpy as np
from scipy.stats import norm


def bs_price(s0, K, r, q, sigma, T, option="call"):
    """Black-Scholes price of a European call or put with continuous dividend yield q.

    call = S0 e^{-qT} N(d1) - K e^{-rT} N(d2)
    put  = K e^{-rT} N(-d2) - S0 e^{-qT} N(-d1)
    """
    sqrt_T = np.sqrt(T)
    d1 = (np.log(s0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    if option == "call":
        return s0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    if option == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - s0 * np.exp(-q * T) * norm.cdf(-d1)
    raise ValueError("option must be 'call' or 'put'")


def down_and_in_put_european(s0, K, H, r, q, sigma, T):
    """Down-and-in put with the barrier observed at maturity only (H < K).

    Payoff (K - S_T) * 1{S_T < H} splits into two pieces with closed forms:
        (H - S_T) * 1{S_T < H}  -> a vanilla put struck at H
        (K - H)   * 1{S_T < H}  -> (K - H) cash-or-nothing digital puts
    """
    d2 = (np.log(s0 / H) + (r - q - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    digital_put = np.exp(-r * T) * norm.cdf(-d2)
    return bs_price(s0, H, r, q, sigma, T, "put") + (K - H) * digital_put