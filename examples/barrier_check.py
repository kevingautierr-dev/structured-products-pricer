"""Compare Monte Carlo and closed-form prices for the down-and-in put (barrier at maturity)."""
from pricer.analytics import down_and_in_put_european
from pricer.engine import mc_price
from pricer.paths import simulate_gbm
from pricer.products import down_and_in_put_payoff_european

S0, K, H, R, Q, SIGMA, T = 100.0, 100.0, 60.0, 0.03, 0.02, 0.25, 1.0

s_T = simulate_gbm(S0, R, Q, SIGMA, T, n_steps=1, n_paths=400_000, seed=11)[:, -1]
mc = mc_price(down_and_in_put_payoff_european(s_T, K, H), R, T)
exact = down_and_in_put_european(S0, K, H, R, Q, SIGMA, T)

n_se = (mc["price"] - exact) / mc["std_err"]
inside = mc["ci_low"] <= exact <= mc["ci_high"]

print(f"Closed form      : {exact:.4f}")
print(f"Monte Carlo      : {mc['price']:.4f}")
print(f"Standard error   : {mc['std_err']:.4f}")
print(f"95% CI           : [{mc['ci_low']:.4f} ; {mc['ci_high']:.4f}]")
print(f"Gap              : {n_se:+.1f} standard errors -> {'inside' if inside else 'OUTSIDE'} the 95% CI")