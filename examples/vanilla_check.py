"""Compare Monte Carlo and Black-Scholes prices for a European call and put."""
from pricer.analytics import bs_price
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import call_payoff, put_payoff

S0, K, R, Q, SIGMA, T = 100.0, 100.0, 0.03, 0.02, 0.25, 1.0

s_T = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=200_000, seed=42)[:, -1]

print(f"{'Option':<6} {'Black-Scholes':>14} {'Monte Carlo':>12} {'Std err':>9} {'Gap (bp)':>9}")
for option, payoff in [("call", call_payoff), ("put", put_payoff)]:
    exact = bs_price(S0, K, R, Q, SIGMA, T, option)
    mc = mc_price(payoff(s_T, K), R, T)
    gap_bp = (mc["price"] - exact) / S0 * 1e4
    print(f"{option:<6} {exact:>14.4f} {mc['price']:>12.4f} {mc['std_err']:>9.4f} {gap_bp:>9.1f}")