import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from povcol.weighted import gini, weighted_quantile, weighted_rate  # noqa: E402


def test_gini_equal_incomes_is_zero():
    assert abs(gini([5, 5, 5, 5])) < 1e-12


def test_gini_one_person_has_everything():
    # population Gini of (0,...,0,1) with n units is 1 - 1/n
    assert abs(gini([0, 0, 0, 1]) - 0.75) < 1e-12


def test_gini_weights_equal_replication():
    rng = np.random.default_rng(0)
    x = rng.lognormal(13, 1, 200)
    w = rng.integers(1, 6, 200)
    assert abs(gini(x, w) - gini(np.repeat(x, w))) < 1e-10


def test_gini_matches_mean_abs_difference_formula():
    rng = np.random.default_rng(1)
    x = rng.lognormal(13, 0.8, 300)
    g_ref = np.abs(x[:, None] - x[None, :]).sum() / (2 * len(x) ** 2 * x.mean())
    assert abs(gini(x) - g_ref) < 1e-10


def test_quantile_matches_numpy_inverted_cdf():
    rng = np.random.default_rng(2)
    x = rng.normal(size=101)
    for q in [0.1, 0.25, 0.5, 0.9]:
        assert weighted_quantile(x, q) == np.quantile(x, q, method="inverted_cdf")


def test_quantile_weights_equal_replication():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    w = np.array([1, 1, 1, 7])
    assert weighted_quantile(x, 0.5, w) == 4.0
    assert weighted_quantile(x, 0.3, w) == np.quantile(np.repeat(x, w), 0.3, method="inverted_cdf")


def test_rate():
    assert weighted_rate([1, 0, 0, 0]) == 25.0
    assert weighted_rate([1, 0], [3, 1]) == 75.0


def test_ratio_se_matches_srs_proportion():
    # one person per unit, equal weights: SE must equal sqrt(p(1-p)/(n-1)) * ... the
    # with-replacement SRS formula sqrt(p(1-p)/n) * sqrt(n/(n-1))
    from povcol.weighted import ratio_se
    rng = np.random.default_rng(3)
    y = (rng.random(2000) < 0.3).astype(float)
    R, se = ratio_se(y, np.ones_like(y), np.ones_like(y))
    p = y.mean()
    n = len(y)
    assert abs(R - p) < 1e-12
    assert abs(se - np.sqrt(p * (1 - p) / (n - 1))) < 1e-12


def test_ratio_se_scale_invariant_in_weights():
    from povcol.weighted import ratio_se
    rng = np.random.default_rng(4)
    x = rng.integers(1, 6, 500).astype(float)
    y = np.minimum(x, rng.integers(0, 4, 500))
    w = rng.uniform(10, 500, 500)
    s = rng.integers(0, 5, 500)
    assert np.allclose(ratio_se(y, x, w, s), ratio_se(y, x, 7 * w, s))
