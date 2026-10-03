"""Convergence of the Monte Carlo price of a European call towards Black-Scholes."""
import matplotlib.pyplot as plt

from pricer.analytics import bs_price
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import call_payoff

S0, K, R, Q, SIGMA, T = 100.0, 100.0, 0.03, 0.02, 0.25, 1.0
N_LIST = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000]

exact = bs_price(S0, K, R, Q, SIGMA, T, "call")
prices, lows, highs = [], [], []
for n in N_LIST:
    s_T = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=n, seed=2024)[:, -1]
    mc = mc_price(call_payoff(s_T, K), R, T)
    prices.append(mc["price"])
    lows.append(mc["ci_low"])
    highs.append(mc["ci_high"])

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.fill_between(N_LIST, lows, highs, color="#16293E", alpha=0.15, label="95% confidence interval")
ax.plot(N_LIST, prices, "o-", color="#16293E", label="Monte Carlo price")
ax.axhline(exact, color="#A9802E", linestyle="--", label=f"Black-Scholes = {exact:.4f}")
ax.set_xscale("log")
ax.set_xlabel("Number of paths (log scale)")
ax.set_ylabel("European call price")
ax.set_title("Monte Carlo convergence: interval shrinks as 1/sqrt(N)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("examples/convergence_call.png", dpi=150)
print("Saved examples/convergence_call.png")
for n, p, lo, hi in zip(N_LIST, prices, lows, highs):
    print(f"N = {n:>7,}  price = {p:.4f}  CI width = {hi - lo:.4f}")