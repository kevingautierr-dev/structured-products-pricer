"""Redemption profiles at maturity: BRC vs Phoenix (case: never autocalled)."""
import matplotlib.pyplot as plt
import numpy as np

perf = np.linspace(0.0, 1.5, 601)          # final performance S_T / S_0
BRC_COUPON, PHX_COUPON = 0.0315, 0.0738 / 4  # fair coupons from the examples

# BRC, barrier 60% observed at maturity: capital + fixed coupon, or capital x perf + coupon
brc = np.where(perf >= 0.60, 100.0, 100.0 * np.minimum(perf, 1.0)) + 100.0 * BRC_COUPON

# Phoenix last date, assuming no autocall and no missed coupon before:
# above 70% -> capital + coupon ; between 60% and 70% -> capital only ; below 60% -> capital x perf
phx = np.where(perf >= 0.70, 100.0 + 100.0 * PHX_COUPON,
               np.where(perf >= 0.60, 100.0, 100.0 * perf))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, y, title, color in [
    (axes[0], brc, "BRC 1y: barrier 60% at maturity", "#16293E"),
    (axes[1], phx, "Phoenix 3y: last observation, not autocalled", "#A9802E"),
]:
    ax.plot(perf * 100, y, color=color, lw=2.2, label="Product")
    ax.plot(perf * 100, 100 * perf, "--", color="grey", lw=1, label="Direct equity holding")
    ax.axvline(60, color="#B4473B", ls=":", lw=1.2, label="Protection barrier 60%")
    ax.set_title(title)
    ax.set_xlabel("Final performance S_T / S_0 (%)")
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 150)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")
axes[0].set_ylabel("Redemption (% of nominal)")
fig.tight_layout()
fig.savefig("examples/payoff_diagrams.png", dpi=150)
print("Saved examples/payoff_diagrams.png")
