import numpy as np


def wmape(y_true, y_pred):
    denominator = np.sum(np.abs(y_true))
    if denominator == 0:
        return np.nan
    return np.sum(np.abs(y_true - y_pred)) / denominator


# LSI/GSI
# single -> small -> small-low-fk -> medium-low-fk -> medium-matching

actual_max_subintensity = np.array([])
predicted_max_subintensity = np.array(
    [
        3297609.23,
        974658,
    ]
)

print("wMAPE:", wmape(actual_max_subintensity, predicted_max_subintensity))
