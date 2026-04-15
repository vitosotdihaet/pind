import numpy as np
from scipy.stats import gamma
from scipy.integrate import quad


def moments_of_max_sum_gamma(k, theta, N, C=0.0):
    """
    Вычисляет матожидание и дисперсию величины Z = max(S_1,...,S_n) + C,
    где S_i ~ Gamma(2k, theta) независимы.
    Параметры:
        k     : параметр формы исходного гамма-распределения
        theta : параметр масштаба
        n     : количество сумм, из которых берётся максимум
        C     : константа, добавляемая к максимуму
    Возвращает:
        (E[Z], Var[Z])
    """
    shape_sum = 2 * k
    scale_sum = theta

    def f_max(m):
        if m < 0:
            return 0.0
        pdf_val = gamma.pdf(m, a=shape_sum, scale=scale_sum)
        cdf_val = gamma.cdf(m, a=shape_sum, scale=scale_sum)
        return N * pdf_val * (cdf_val ** (N - 1))

    E_M, _ = quad(lambda m: m * f_max(m), 0, np.inf, limit=200)
    E_M2, _ = quad(lambda m: m**2 * f_max(m), 0, np.inf, limit=200)

    var_M = E_M2 - E_M**2

    E_Z = E_M + C
    var_Z = var_M
    return E_Z, var_Z


# network latency parameters
k = 2.5
theta = 1.5
# replicaset count
N = 10
# deterministic part
C = 5.0

mean_Z, var_Z = moments_of_max_sum_gamma(k, theta, N, C)
print(f"E[Z] = {mean_Z:.6f}")
print(f"Var[Z] = {var_Z:.6f}")
