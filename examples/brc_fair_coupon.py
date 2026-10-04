"""Fair coupon of a 1-year Barrier Reverse Convertible (barrier 60%, issuer margin 1%)."""
import numpy as np

from pricer.analytics import bgk_shift, brc_price
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import brc_payoff
from pricer.solver import fair_coupon

S0, R, Q, SIGMA, T = 100.0, 0.03, 0.02, 0.25, 1.0
BARRIER, NOMINAL, MARGIN = 0.60, 100.0, 0.01
TARGET = NOMINAL * (1 - MARGIN)
N_STEPS = 252

terminal = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=400_000, seed=21)
daily = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=N_STEPS, n_paths=60_000, seed=5)
barrier_bgk = bgk_shift(BARRIER, SIGMA, T / N_STEPS)  # barrier in % of S0, shifted up

cases = [
    ("Barrier at maturity", "maturity", terminal, BARRIER),
    ("Continuous barrier, BGK", "continuous", daily, barrier_bgk),
]

print(f"Target price: {TARGET:.0f}% of nominal (issuer margin {MARGIN:.0%})\n")
print(f"{'Case':<26} {'Closed form':>12} {'Monte Carlo':>12} {'MC std err':>11}")
for label, monitoring, paths, barrier in cases:
    c_exact = fair_coupon(lambda c: brc_price(S0, BARRIER, c, R, Q, SIGMA, T, monitoring=monitoring), TARGET)

    def mc(c):
        return mc_price(brc_payoff(paths, S0, barrier, c, monitoring=monitoring), R, T)

    c_mc = fair_coupon(lambda c: mc(c)["price"], TARGET)
    se = mc(c_mc)["std_err"] / (NOMINAL * np.exp(-R * T))
    print(f"{label:<26} {c_exact:>11.2%} {c_mc:>12.2%} {se:>10.2%}")

print("\nDecomposition check (barrier at maturity, coupon 5%):")
zc = NOMINAL * np.exp(-R * T)
coupon_pv = NOMINAL * 0.05 * np.exp(-R * T)
put = zc + coupon_pv - brc_price(S0, BARRIER, 0.05, R, Q, SIGMA, T)
print(f"  zero-coupon {zc:.2f} + coupon PV {coupon_pv:.2f} - put {put:.2f} = {zc + coupon_pv - put:.2f}")