"""Fair coupon of a 3-year Phoenix autocall with memory coupon (quarterly observations)."""
import numpy as np

from pricer.engine import mc_estimate
from pricer.paths import simulate_gbm
from pricer.products import phoenix_pv
from pricer.solver import fair_coupon

S0, R, Q = 100.0, 0.03, 0.02
T, N_OBS, N_PATHS = 3.0, 12, 200_000
TIMES = np.linspace(T / N_OBS, T, N_OBS)   # 0.25, 0.50, ..., 3.00
TARGET = 99.0                               # 100% minus 1% issuer margin

print("Phoenix 3y quarterly | autocall 100% | coupon barrier 70% | protection 60%")
print(f"Target price {TARGET:.0f}% | {N_PATHS:,} paths\n")
print(f"{'Vol':>5} {'Memory':>8} {'Coupon/qtr':>11} {'Coupon p.a.':>12} {'Std err p.a.':>13} {'Avg life (y)':>13}")

for sigma in (0.15, 0.25, 0.35):
    perf = simulate_gbm(S0, R, Q, sigma, T, N_OBS, N_PATHS, seed=8)[:, 1:] / S0
    for memory in (True, False):
        def mc(c):
            return mc_estimate(phoenix_pv(perf, TIMES, R, c, memory=memory))

        c = fair_coupon(lambda c: mc(c)["price"], TARGET)
        # std error in coupon units: price error divided by the price sensitivity to the coupon
        dprice_dc = (mc(c + 1e-4)["price"] - mc(c)["price"]) / 1e-4
        se_pa = 4 * mc(c)["std_err"] / dprice_dc

        # expected life: first autocall date, or maturity if never called
        called = perf[:, :-1] >= 1.0
        first_call = np.where(called.any(axis=1), called.argmax(axis=1), N_OBS - 1)
        avg_life = TIMES[first_call].mean()

        print(f"{sigma:>5.0%} {'yes' if memory else 'no':>8} {c:>11.2%} {4 * c:>12.2%} {se_pa:>13.2%} {avg_life:>13.2f}")