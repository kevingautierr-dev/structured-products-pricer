"""Payoff functions. Each takes simulated prices and returns one payoff per path."""
import numpy as np


def call_payoff(s_T, K):
    """European call payoff: max(S_T - K, 0) for each path."""
    return np.maximum(s_T - K, 0.0)


def put_payoff(s_T, K):
    """European put payoff: max(K - S_T, 0) for each path."""
    return np.maximum(K - s_T, 0.0)


def down_and_in_put_payoff_european(s_T, K, H):
    """Down-and-in put, barrier observed at maturity only.
    Pays K - S_T if S_T < H, else 0."""
    return np.where(s_T < H, K - s_T, 0.0)