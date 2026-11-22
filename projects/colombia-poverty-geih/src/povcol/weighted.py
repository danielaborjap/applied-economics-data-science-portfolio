"""Weighted statistics written from scratch (no survey library).

All functions take a value array `x` and a weight array `w` (DANE expansion
factors, possibly multiplied by household size). NaNs are dropped pairwise.
"""
from __future__ import annotations

import numpy as np


def _clean(x, w=None):
    x = np.asarray(x, dtype=float)
    w = np.ones_like(x) if w is None else np.asarray(w, dtype=float)
    if x.shape != w.shape:
        raise ValueError("x and w must have the same shape")
    keep = ~(np.isnan(x) | np.isnan(w))
    x, w = x[keep], w[keep]
    if (w < 0).any():
        raise ValueError("weights must be non-negative")
    if w.sum() == 0:
        raise ValueError("weights sum to zero")
    return x, w


def weighted_mean(x, w=None) -> float:
    x, w = _clean(x, w)
    return float(np.sum(x * w) / np.sum(w))


def weighted_rate(flag, w=None) -> float:
    """Share (0-100) of the weighted population with flag == 1."""
    return 100.0 * weighted_mean(np.asarray(flag, dtype=float), w)


def weighted_quantile(x, q, w=None):
    """Weighted quantile(s), q in [0, 1].

    Uses the inverse of the weighted empirical CDF: the smallest x whose
    cumulative weight share reaches q. With equal weights this equals
    numpy's `inverted_cdf` method.
    """
    x, w = _clean(x, w)
    order = np.argsort(x, kind="mergesort")
    x, w = x[order], w[order]
    cdf = np.cumsum(w) / np.sum(w)
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    if ((q_arr < 0) | (q_arr > 1)).any():
        raise ValueError("q must be in [0, 1]")
    idx = np.searchsorted(cdf, q_arr - 1e-12, side="left")
    idx = np.clip(idx, 0, len(x) - 1)
    out = x[idx]
    return float(out[0]) if np.ndim(q) == 0 else out


def gini(x, w=None) -> float:
    """Weighted Gini coefficient.

    Computed from the Lorenz curve with the trapezoid rule:
        G = 1 - sum_i p_i (L_i + L_{i-1})
    where p_i is unit i's population share and L_i the cumulative income share.
    Exact for grouped data; with equal weights it equals the standard
    (n-1)/n-free "population" Gini.
    """
    x, w = _clean(x, w)
    if (x < 0).any():
        raise ValueError("Gini expects non-negative incomes")
    order = np.argsort(x, kind="mergesort")
    x, w = x[order], w[order]
    p = w / w.sum()
    income = x * w
    L = np.cumsum(income) / income.sum()
    L_prev = np.concatenate(([0.0], L[:-1]))
    return float(1.0 - np.sum(p * (L + L_prev)))


def ratio_se(y, x, w, strata=None) -> tuple[float, float]:
    """Ratio estimate R = sum(w*y) / sum(w*x) and its linearized standard error.

    Taylor linearization with households as the sampling units and optional strata,
    using the with-replacement variance formula within each stratum:
        z_i = w_i (y_i - R x_i) / sum(w x)
        V(R) = sum_h n_h/(n_h-1) * sum_i (z_hi - zbar_h)^2

    For poverty: y = poor persons in the household (pobre * nper), x = persons (nper),
    w = expansion factor. NOTE: the public GEIH file has no PSU/cluster identifiers,
    so this ignores clustering and will usually UNDERSTATE the true standard error.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    X = np.sum(w * x)
    R = np.sum(w * y) / X
    z = w * (y - R * x) / X
    strata = np.zeros(len(z), dtype=int) if strata is None else np.asarray(strata)
    var = 0.0
    for h in np.unique(strata):
        zh = z[strata == h]
        n = len(zh)
        if n > 1:
            var += n / (n - 1) * np.sum((zh - zh.mean()) ** 2)
    return float(R), float(np.sqrt(var))
