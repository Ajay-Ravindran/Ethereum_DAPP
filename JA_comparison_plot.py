import matplotlib.pyplot as plt
 
x = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

# Cumulative ratio of successful transaction for 3 runs by varying the total number of Joint Accounts in the network
y1 = [0.6, 0.57, 0.5366666666666666, 0.5475, 0.528, 0.525, 0.5285714285714286, 0.52375, 0.5166666666666667, 0.519]      # For 334 Joint Accounts
y2 = [0.55, 0.525, 0.49666666666666665, 0.4925, 0.502, 0.5016666666666667, 0.5085714285714286, 0.50375, 0.5, 0.497]     # For 234 Joint Accounts
y3 = [0.54, 0.51, 0.47, 0.4475, 0.432, 0.4266666666666667, 0.4257142857142857, 0.41, 0.42, 0.42]                        # For 141 Joint Accounts

plt.title("Ratio of successful transactions")
plt.xlabel("Total number of transactions")
plt.ylabel("Fraction of successful transactions")

plt.plot(x, y1, label = "334 Joint Accounts", marker = "o")
plt.plot(x,y2, label = "234 Joint Accounts", marker = "h", linestyle='dashdot')
plt.plot(x, y3, label = "141 Joint Accounts", marker = "P", linestyle='--')
plt.legend()
plt.savefig('JA_comparison.png')
plt.show()