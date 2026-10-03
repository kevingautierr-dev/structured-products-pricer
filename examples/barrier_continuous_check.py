"""Continuous down-and-in put: daily Monte Carlo with and without the BGK correction."""
import time

from pricer.analytics import bgk_shift, down_and_in_put_continuous
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import down_and_in_put_payoff_continuous

S0, K, H, R, Q, SIGMA, T = 100.0, 100.0, 60.0, 0.03, 0.02, 0.25, 1.0
N_STEPS, N_PATHS = 252, 60_000

start = time.time()
paths = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=N_STEPS, n_paths=N_PATHS, seed=5)
exact = down_and_in_put_continuous(S0, K, H, R, Q, SIGMA, T)
h_adj = bgk_shift(H, SIGMA, T / N_STEPS)

print(f"Closed form (Reiner-Rubinstein): {exact:.4f}")
print(f"BGK-shifted barrier            : {h_adj:.3f}  (instead of {H:.0f})\n")
print(f"{'Method':<26} {'MC price':>9} {'Std err':>8} {'Gap (bp)':>9} {'Gap / SE':>9}")
for label, barrier in [("Daily, no correction", H), ("Daily + BGK correction", h_adj)]:
    mc = mc_price(down_and_in_put_payoff_continuous(paths, K, barrier), R, T)
    gap = mc["price"] - exact
    print(f"{label:<26} {mc['price']:>9.4f} {mc['std_err']:>8.4f} {gap / S0 * 1e4:>9.1f} {gap / mc['std_err']:>9.1f}")
print(f"\n{N_PATHS:,} paths x {N_STEPS} daily steps in {time.time() - start:.1f} s")