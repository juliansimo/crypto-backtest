import numpy as np
import statistics as stats
# import matplotlib.pyplot as plt

# parâmetros do ativo
S0 = 115000  # preço inicial
mu = 0.1  # retorno anual esperado
sigma = 0.6  # volatilidade anual (ex: 60% para cripto)
T = 5  # tempo total (1 ano)
dt = 1/252  # passo de tempo (diário)
N = int(T/dt)  # número de passos
n_sim = 1000  # número de simulações

# simulação
np.random.seed(42)
t = np.linspace(0, T, N)
trajectories = np.zeros((n_sim, N))
for i in range(n_sim):
    W = np.random.standard_normal(size=N)
    W = np.cumsum(W) * np.sqrt(dt)
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    trajectories[i] = S0 * np.exp(X)

print(stats.mean(trajectories[:,-1]))
print(stats.stdev(trajectories[:,-1]))

# for i in range(len(trajectories)):

# plot
# plt.figure(figsize=(12,6))
# for i in range(n_sim):
#     plt.plot(t, trajectories[i])
# plt.title("Simulação de Preços (GBM)")
# plt.xlabel("Tempo (anos)")
# plt.ylabel("Preço")
# plt.grid(True)
# plt.show()
