import scipy
import scipy.integrate
from scipy.special import gammainc, gammaincc
from scipy.stats import gamma as gamma_dist


def prob_timeout_search_LSI(
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
) -> float:
    """
    Вычисляет P(#time_user_search_LSI >= #timeout).
    """
    # детерминированная часть
    net_delay = (
        query_size + pk_per_fk_card * replicaset_count * row_size
    ) / user_net_speed
    deterministic_part = queue_time_execute + deterministic_tcsi + net_delay

    tau = timeout - deterministic_part

    if tau <= 0:
        return 1.0

    k1 = 2 * user_time_k
    theta1 = user_time_theta
    k2 = 2 * cluster_time_k
    theta2 = cluster_time_theta

    # плотность гамма-распределения
    def user_to_coordinator_pdf(t):
        return gamma_dist.pdf(t, a=k1, scale=theta1)

    # максимум гамма-распределений
    def coordinator_to_executors_max_cdf(x):
        if x <= 0:
            return 0.0
        return gammainc(k2, x / theta2) ** replicaset_count

    # первое слагаемое
    def integrand(t: float):
        return user_to_coordinator_pdf(t) * (
            1.0 - coordinator_to_executors_max_cdf(tau - t)
        )

    # интегрирование от 0 до tau
    integral_part, _ = scipy.integrate.quad(
        integrand, 0, tau, limit=200, epsabs=1e-12, epsrel=1e-12
    )

    # второе слагаемое
    tail_part = gammaincc(k1, tau / theta1)

    return integral_part + tail_part


def prob_timeout_search_GSI(
    timeout,
    user_time_k,
    user_time_theta,
    cluster_time_k,
    cluster_time_theta,
    # параметры детерминированной части
    deterministic_tus,
    replicaset_count_with_fk,
) -> float:
    """
    Вычисляет P(#time_user_search_GSI >= #timeout).
    """
    # детерминированная часть
    tau = timeout - deterministic_tus

    if tau <= 0:
        return 1.0

    k1 = 2 * user_time_k
    theta1 = user_time_theta

    k2 = 2 * cluster_time_k
    theta2 = cluster_time_theta

    # гамма-распределения времени между пользователем и координатором
    def user_to_coordinator_pdf(t):
        return gamma_dist.pdf(t, a=k1, scale=theta1)

    # гамма-распределения между координатором и исполнителем со вторичным ключом
    def coordinator_to_fk_executor_pdf(t):
        return gamma_dist.pdf(t, a=k2, scale=theta2)

    # гамма-распределения между пользователем и исполнителем со вторичным ключом
    def user_to_fk_executor_pdf(t):
        if t <= 0:
            return 0.0
        val, _ = scipy.integrate.quad(
            lambda s: (
                user_to_coordinator_pdf(s) * coordinator_to_fk_executor_pdf(t - s)
            ),
            0,
            t,
            limit=1000,
            epsabs=1e-10,
            epsrel=1e-10,
        )
        return val

    def user_to_fk_executor_cdf(t):
        if t <= 0:
            return 0.0
        val, _ = scipy.integrate.quad(
            user_to_fk_executor_pdf,
            0,
            t,
            limit=1000,
            epsabs=1e-10,
            epsrel=1e-10,
        )
        return val

    # максимум гамма-распределений
    def fk_executor_to_executors_max_pdf(x):
        if x <= 0:
            return 0.0
        return gammainc(k2, x / theta2) ** replicaset_count_with_fk

    # первое слагаемое
    def integrand(t: float):
        return user_to_fk_executor_pdf(t) * (
            1.0 - fk_executor_to_executors_max_pdf(tau - t)
        )

    # интегрирование от 0 до tau
    integral_part, _ = scipy.integrate.quad(
        integrand, 0, tau, limit=200, epsabs=1e-12, epsrel=1e-12
    )

    # второе слагаемое
    tail_part = 1 - user_to_fk_executor_cdf(tau)

    return integral_part + tail_part
