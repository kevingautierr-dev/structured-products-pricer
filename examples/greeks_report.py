"""Greeks of a call (validation), a BRC and a Phoenix by bump-and-revalue."""
import numpy as np

from pricer.analytics import bs_greeks
from pricer.engine import mc_estimate, mc_price
from pricer.greeks import bump_greeks
from pricer.paths import simulate_gbm
from pricer.products import brc_payoff, call_payoff, phoenix_pv

S0, Q, SIGMA, R = 100.0, 0.02, 0.25, 0.03
SEED = 7  # same seed for every bumped scenario = common random numbers


def call_price(s0, sigma, r):
    s_T = simulate_gbm(s0, r, Q, sigma, 1.0, 1, 400_000, seed=SEED)[:, -1]
    return mc_price(call_payoff(s_T, 100.0), r, 1.0)["price"]


def brc_price(s0, sigma, r):
    # strike and barrier stay fixed at 100 / 60: only the spot moves
    paths = simulate_gbm(s0, r, Q, sigma, 1.0, 1, 400_000, seed=SEED)
    return mc_price(brc_payoff(paths, 100.0, 0.60, coupon=0.0315), r, 1.0)["price"]


TIMES = np.linspace(0.25, 3.0, 12)


def phoenix_price(s0, sigma, r):
    paths = simulate_gbm(s0, r, Q, sigma, 3.0, 12, 200_000, seed=SEED)
    return mc_estimate(phoenix_pv(paths[:, 1:] / 100.0, TIMES, r, coupon=0.0184))["price"]


bs = bs_greeks(S0, 100.0, R, Q, SIGMA, 1.0)
rows = [
    ("Call 1y (Black-Scholes)", {"price": np.nan, **bs}),
    ("Call 1y (Monte Carlo)", bump_greeks(call_price, S0, SIGMA, R)),
    ("BRC 1y, barrier 60%", bump_greeks(brc_price, S0, SIGMA, R)),
    ("Phoenix 3y, memory", bump_greeks(phoenix_price, S0, SIGMA, R)),
]

print("Greeks per 100 nominal | vega per +1 vol point | rho per +1 bp\n")
print(f"{'Product':<26} {'Price':>8} {'Delta':>8} {'Gamma':>8} {'Vega':>8} {'Rho':>8}")
for name, g in rows:
    price = "-" if np.isnan(g["price"]) else f"{g['price']:.2f}"
    print(f"{name:<26} {price:>8} {g['delta']:>8.3f} {g['gamma']:>8.4f} {g['vega']:>8.3f} {g['rho']:>8.4f}")