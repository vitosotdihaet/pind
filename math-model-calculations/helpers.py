import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve


class RV:
    def __init__(self, x, pdf, cdf):
        self.x = x
        self.pdf = pdf
        self.cdf = cdf
        self._pdf_interp = interp1d(
            x, pdf, kind="linear", bounds_error=False, fill_value=0.0
        )
        self._cdf_interp = interp1d(
            x, cdf, kind="linear", bounds_error=False, fill_value=(0.0, 1.0)
        )

    def pdf_at(self, z):
        return self._pdf_interp(z)

    def cdf_at(self, z):
        return self._cdf_interp(z)

    def shift(self, c):
        new_x = self.x + c
        return RV(new_x, self.pdf, self.cdf)

    def __add__(self, other):
        # шаг исходных сеток (должны быть одинаковы)
        dx = self.x[1] - self.x[0]
        pdf_conv = fftconvolve(self.pdf, other.pdf, mode="full") * dx

        # строим новую сетку точно той же длины, что и свёртка
        start = self.x[0] + other.x[0]
        stop = self.x[-1] + other.x[-1]
        new_x = np.linspace(start, stop, len(pdf_conv))

        cdf_conv = np.cumsum(pdf_conv) * dx
        cdf_conv = np.clip(cdf_conv, 0, 1)
        return RV(new_x, pdf_conv, cdf_conv)

    @staticmethod
    def maximum(*rvs):
        # определяем общую равномерную сетку для всех
        x_min = max(rv.x[0] for rv in rvs)
        x_max = min(rv.x[-1] for rv in rvs)
        n_points = min(len(rv.x) for rv in rvs)  # или фиксированное число
        x = np.linspace(x_min, x_max, n_points)

        cdfs = [rv.cdf_at(x) for rv in rvs]
        pdfs = [rv.pdf_at(x) for rv in rvs]

        n = len(rvs)
        pdf_max = np.zeros_like(x)
        for i in range(n):
            prod_cdf = np.ones_like(x)
            for j in range(n):
                if j != i:
                    prod_cdf *= cdfs[j]
            pdf_max += pdfs[i] * prod_cdf

        cdf_max = np.prod(cdfs, axis=0)
        return RV(x, pdf_max, cdf_max)

    def mean(self):
        dx = self.x[1] - self.x[0]
        return np.sum(self.x * self.pdf) * dx
