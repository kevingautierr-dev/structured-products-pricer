"""Fair coupon of a worst-of Phoenix (3 assets) as a function of correlation."""
import matplotlib.pyplot as plt
import numpy as np

from pricer.engine import mc_estimate
from pricer.paths import constant_corr_matrix, simulate_gbm, simulate_gbm_multi
from pricer.products import phoenix_pv
from pricer.solver import fair_coupon

R, T, N_OBS, N_PATHS = 0.03, 3.0, 12, 100_000
TIMES = np.linspace(T / N_OBS, T, N_OBS)
S0 = np.array([100.0, 100.0, 100.0])
Q = np.array([0.02, 0.02, 0.02])
SIGMA = np.array([0.25, 0.25, 0.25])
TARGET = 99.0


def fair(perf):
    return 4 * fair_coupon(lambda c: mc_estimate(phoenix_pv(perf, TIMES, R, c))["price"], TARGET)


single = simulate_gbm(100.0, R, 0.02, 0.25, T, N_OBS, N_PATHS, seed=8)[:, 1:] / 100.0
c_single = fair(single)
print(f"Single underlying (vol 25%)          : {c_single:.2%} p.a.")

rhos = [0.0, 0.2, 0.4, 0.6, 0.8, 0.95]
coupons = []
for rho in rhos:
    paths = simulate_gbm_multi(S0, R, Q, SIGMA, constant_corr_matrix(3, rho), T, N_OBS, N_PATHS, seed=8)
    worst = (paths[:, 1:, :] / S0).min(axis=2)   # worst performance of the basket at each date
    coupons.append(fair(worst))
    print(f"Worst-of 3, correlation {rho:>4.0%}        : {coupons[-1]:.2%} p.a.")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(rhos, [c * 100 for c in coupons], "o-", color="#16293E", label="Worst-of 3 assets")
ax.axhline(c_single * 100, color="#A9802E", linestyle="--", label="Single underlying")
ax.set_xlabel("Pairwise correlation")
ax.set_ylabel("Fair coupon (% p.a.)")
ax.set_title("Worst-of Phoenix: lower correlation, higher coupon")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("examples/worst_of_correlation.png", dpi=150)
print("\nSaved examples/worst_of_correlation.png")