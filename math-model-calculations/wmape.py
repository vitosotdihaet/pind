import numpy as np


def wmape(y_true, y_pred):
    denominator = np.sum(np.abs(y_true))
    if denominator == 0:
        return np.nan
    return np.sum(np.abs(y_true - y_pred)) / denominator


# LSI/GSI
# single -> small -> small-low-fk -> medium-low-fk -> medium-matching

actual_max_subintensity = np.array(
    [
        3486.15,
        3565.3 * 2,
        305.27,
        2710.03 / (5) * 4,
    ]
)
predicted_max_subintensity = np.array(
    [
        3297609.23,
        974658,
        3297609.23,
        748643.08,
    ]
)

print("max_sub:", wmape(actual_max_subintensity, predicted_max_subintensity))


actual_mean_t_user = np.array(
    [
        0.0379,
        0.0338,
        0.0646,
        0.0654,
    ]
)
predicted_mean_t_user = np.array(
    [0.0260817333, 0.0371653221, 0.0337325714, 0.0463350764]
)
print("mean_t_user:", wmape(actual_mean_t_user, predicted_mean_t_user))


actual_prob_timeout = np.array(
    [
        0.000000008231,
        0.000000000576,
        0.00000000582,
        0.000000009173,
    ]
)
predicted_prob_timeout = np.array(
    [
        0.000000005719,
        0.000000000631,
        0.00000000312,
        0.00000000101,
    ]
)
print("prob_timeout:", wmape(actual_prob_timeout, predicted_prob_timeout))


actual_queue_time = np.array(
    [
        0.0000000185,
        0.0000000021,
        0.0000000998,
        0.0000000941,
    ]
)
predicted_queue_time = np.array(
    [
        0.0000001205,
        0.0000000937,
        0.00000009028,
        0.00000000101,
    ]
)
print("queue_time:", wmape(actual_queue_time, predicted_queue_time))
