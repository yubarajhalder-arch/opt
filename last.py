import matplotlib.pyplot as plt

# Parameters
fair_value = 40
algo_buy = 20
algo_sell = 80
human_order_price = 21
algo_prices = [algo_buy]
human_prices = [None]
steps = []

# Algo reacts when human trades
step = 0
while algo_buy < fair_value:
    step += 1
    algo_buy += 1  # Algo raises buy
    algo_sell = 100 - algo_buy  # Keep wide spread
    steps.append(step)
    algo_prices.append(algo_buy)
    human_prices.append(human_order_price)

# Human chases above fair value by 20%
human_buy_price = fair_value * 1.2
step += 1
steps.append(step)
algo_prices.append(fair_value)
human_prices.append(human_buy_price)

# Algo sells at 20% above fair value
algo_sell_price = human_buy_price
human_loss = human_buy_price - fair_value

print(f"Human bought at ₹{human_buy_price}, fair value ₹{fair_value}, loss = ₹{human_loss}")

# Plotting the behavior
plt.figure(figsize=(10,5))
plt.plot(steps, algo_prices, label='Algo Buy Price', color='green', marker='o')
plt.plot(steps, human_prices, label='Human Action', color='red', linestyle='--', marker='x')
plt.axhline(fair_value, color='blue', linestyle=':', label='Fair Value')
plt.axhline(fair_value * 1.2, color='orange', linestyle='--', label='20% above Fair Value')

plt.title("Non-Liquid Option Manipulation Simulation")
plt.xlabel("Step / Reaction Cycle")
plt.ylabel("Price (₹)")
plt.legend()
plt.grid(True)
plt.show()
