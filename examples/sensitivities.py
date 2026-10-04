"""Fair coupon sensitivities: volatility and barrier level, for the BRC and the Phoenix."""
import matplotlib.pyplot as plt
import numpy as np

from pricer.analytics import brc_price
from pricer.engine import mc_estimate
from pricer.paths import simulate_gbm
from pricer.products import phoenix_pv
from pricer.solver import fair_coupon

S0, R, Q, TARGET = 100.0, 0.03, 0.02, 99.0
TIMES = np.linspace(0.25, 3.0, 12)
VOLS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
BARRIERS = [0.50, 0.55, 0.60, 0.65, 0.70]


def brc_coupon(sigma, barrier):
    """Closed form, barrier observed at maturity: exact and instant."""
    return fair_coupon(lambda c: brc_price(S0, barrier, c, R, Q, sigma, 1.0), TARGET)


def phoenix_coupon(sigma, protection, n_paths=100_000):
    """Monte Carlo, coupon per annum (4 quarterly coupons)."""
    perf = simulate_gbm(S0, R, Q, sigma, 3.0, 12, n_paths, seed=8)[:, 1:] / S0
    price = lambda c: mc_estimate(phoenix_pv(perf, TIMES, R, c, protection_barrier=protection))["price"]
    return 4 * fair_coupon(price, TARGET)


vol_brc = [brc_coupon(s, 0.60) for s in VOLS]
vol_phx = [phoenix_coupon(s, 0.60) for s in VOLS]
bar_brc = [brc_coupon(0.25, b) for b in BARRIERS]
bar_phx = [phoenix_coupon(0.25, b) for b in BARRIERS]

print(f"{'Vol':>6} {'BRC coupon':>11} {'Phoenix p.a.':>13}")
for s, b, p in zip(VOLS, vol_brc, vol_phx):
    print(f"{s:>6.0%} {b:>11.2%} {p:>13.2%}")
print(f"\n{'Barrier':>8} {'BRC coupon':>11} {'Phoenix p.a.':>13}   (protection barrier, vol 25%)")
for x, b, p in zip(BARRIERS, bar_brc, bar_phx):
    print(f"{x:>8.0%} {b:>11.2%} {p:>13.2%}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, x, brc, phx, label in [
    (axes[0], VOLS, vol_brc, vol_phx, "Volatility"),
    (axes[1], BARRIERS, bar_brc, bar_phx, "Protection barrier"),
]:
    ax.plot([v * 100 for v in x], [c * 100 for c in brc], "o-", color="#16293E", label="BRC 1y")
    ax.plot([v * 100 for v in x], [c * 100 for c in phx], "s-", color="#A9802E", label="Phoenix 3y (p.a.)")
    ax.set_xlabel(label + " (%)")
    ax.set_ylabel("Fair coupon (% p.a.)")
    ax.grid(alpha=0.3)
    ax.legend()
axes[0].set_title("Higher volatility, higher coupon")
axes[1].set_title("Higher barrier, higher coupon")
fig.tight_layout()
fig.savefig("examples/sensitivities.png", dpi=150)
print("\nSaved examples/sensitivities.png")