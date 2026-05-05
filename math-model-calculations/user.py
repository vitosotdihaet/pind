from scipy.integrate import quad
from scipy.special import gammainc, gammaincc
from scipy.stats import gamma as gamma_dist


def prob_timeout(
    timeout,
    user_time_k,
    user_time_theta,
    cluster_time_k,
    cluster_time_theta,
    # параметры детерминированной части
    queue_time_execute,
    deterministic_tcsi,
    query_size,
    pk_per_fk_card,
    replicaset_count,
    row_size,
    user_net_speed,
):
    """
    Вычисляет P(#time_user_search_LSI >= #timeout).
    """
    # 1. Детерминированная часть
    net_delay = (
        query_size + pk_per_fk_card * replicaset_count * row_size
    ) / user_net_speed
    deterministic_part = queue_time_execute + deterministic_tcsi + net_delay

    tau = timeout - deterministic_part

    if tau <= 0:
        return 1.0

    # 2. Параметры гамма-распределений
    alpha1 = 2 * user_time_k
    theta1 = user_time_theta
    alpha2 = 2 * cluster_time_k
    theta2 = cluster_time_theta

    # Функция распределения (CDF) гамма-распределения
    def F_gamma(x, alpha, theta):
        # gammainc - регулярзированная нижняя неполная гамма-функция
        return gammainc(alpha, x / theta)

    # Плотность гамма-распределения (можно через scipy.stats)
    def f_T1(t):
        return gamma_dist.pdf(t, a=alpha1, scale=theta1)

    # CDF максимума N величин
    def F_max(x):
        # если x <= 0, CDF = 0
        if x <= 0:
            return 0.0
        return F_gamma(x, alpha2, theta2) ** replicaset_count

    # 3. Подынтегральное выражение для первого слагаемого
    def integrand(t):
        # f_T1(t) * (1 - F_max(tau - t))
        return f_T1(t) * (1.0 - F_max(tau - t))

    # Интегрирование от 0 до tau
    integral_part, _ = quad(integrand, 0, tau, limit=200, epsabs=1e-12, epsrel=1e-12)

    # 4. Второе слагаемое: P(T1 > tau) = 1 - F_T1(tau) = gammaincc(alpha1, tau/theta1)
    tail_part = gammaincc(alpha1, tau / theta1)

    prob = integral_part + tail_part

    # На всякий случай обрежем до [0,1]
    return max(0.0, min(1.0, prob))
