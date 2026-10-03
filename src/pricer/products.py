"""Payoff functions. Each takes simulated prices and returns one payoff per path."""
import numpy as np


def call_payoff(s_T, K):
    """European call payoff: max(S_T - K, 0) for each path."""
    return np.maximum(s_T - K, 0.0)


def put_payoff(s_T, K):
    """European put payoff: max(K - S_T, 0) for each path."""
    return np.maximum(K - s_T, 0.0)