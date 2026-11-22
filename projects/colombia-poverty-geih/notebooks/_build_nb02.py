"""Builds 02_replicate.ipynb (kept so the notebook is reproducible from source)."""
import json
from pathlib import Path

cells = []


def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})


def code(s):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": s.strip("\n")})


md("""
# 02 · Replicate DANE's 2025 monetary poverty and Gini

**Question:** starting from the microdata, do we get DANE's published 2025 figures?
**Target:** each estimate rounds to DANE's published value (1 decimal for rates, 3 for Gini).

Definitions used (from DANE's methodology and the 2025 data dictionary):
- income concept = per-capita income of the **spending unit** (*unidad de gasto*, UG: the household
  minus domestic workers, pensioners and their relatives living in it)
- unit of analysis = **all persons in the household**, each assigned the UG's per-capita income,
  so each household row represents `fex_c × nper` persons
  (weighting by `npersug` instead gives 28.05% / Gini 0.530; `nper` reproduces DANE exactly)
- `pobre` = 1 if `ingpcug < lp`; `indigente` = 1 if `ingpcug < li` (lines vary across 50 domains)
- `clase` 1 = cabeceras (urban), 2 = centros poblados y rural disperso
""")

code("""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

from povcol.load import load
from povcol.weighted import weighted_rate, gini
from povcol import official

YEAR = 2025
RESULTS = ROOT / "results"; RESULTS.mkdir(exist_ok=True)
FIGS = ROOT / "figures"; FIGS.mkdir(exist_ok=True)

hog = load(YEAR, "hogares")
hog["w_person"] = hog["fex"] * hog["nper"]
DOMAINS = {"nacional": hog, "cabeceras": hog[hog["clase"] == 1], "rural": hog[hog["clase"] == 2]}
""")

md("## 1. Replication table")

code("""
rows = []
for dom, d in DOMAINS.items():
    w = d["w_person"]
    mine = {
        "Monetary poverty (%)": weighted_rate(d["pobre"], w),
        "Extreme poverty (%)": weighted_rate(d["indigente"], w),
        "Gini": gini(d["ingpcug"], w),
    }
    dane = {
        "Monetary poverty (%)": official.POVERTY[(YEAR, dom)],
        "Extreme poverty (%)": official.EXTREME[(YEAR, dom)],
        "Gini": official.GINI[(YEAR, dom)],
    }
    for ind in mine:
        rows.append({"domain": dom, "indicator": ind, "this_repo": mine[ind], "DANE": dane[ind]})

rep = pd.DataFrame(rows)
rep["difference"] = rep["this_repo"] - rep["DANE"]
rep["rounds_to_DANE"] = np.where(rep["indicator"] == "Gini",
                                 rep["this_repo"].round(3) == rep["DANE"],
                                 rep["this_repo"].round(1) == rep["DANE"])
rep.to_csv(RESULTS / "replication_2025.csv", index=False)
rep.round(3)
""")

md("""
**Cross-check with a second variable.** The file also has `npobres` (number of poor persons in
the household). Computing the rate from it is an independent route to the same number.
""")

code("""
w = hog["w_person"]
via_flag = weighted_rate(hog["pobre"], w)
via_count = 100 * (hog["fex"] * hog["npobres"]).sum() / w.sum()
print(f"via pobre flag:  {via_flag:.3f}%")
print(f"via npobres:     {via_count:.3f}%")
""")

md("""
## 2. Why the weights matter

Four ways to compute "the" national poverty rate from the same file. Only the last one is the
population estimate. The others make one or both of two mistakes:
- **wrong unit** — counting households instead of persons (poor households are larger)
- **no weights** — treating every sampled household as representing the same number of people
""")

code("""
d = hog
methods = pd.DataFrame({
    "method": [
        "Unweighted, households (row mean)",
        "Weighted, households (fex only)",
        "Unweighted, persons (nper only)",
        "Weighted, persons (fex × nper)  ← official",
    ],
    "rate": [
        weighted_rate(d["pobre"]),
        weighted_rate(d["pobre"], d["fex"]),
        weighted_rate(d["pobre"], d["nper"]),
        weighted_rate(d["pobre"], d["w_person"]),
    ],
})
methods["gap_vs_official_pp"] = methods["rate"] - official.POVERTY[(YEAR, "nacional")]
methods.to_csv(RESULTS / "weights_comparison_2025.csv", index=False)
methods.round(2)
""")

md("""
**Where the bias comes from: the sample is not proportional to the population.**
DANE oversamples the 23 capital cities (each gets ~6,000–12,000 households regardless of size)
and rural areas get a smaller share of the sample than of the population.
""")

code("""
by_domain = (hog.groupby("dominio")
                .agg(sample_households=("pobre", "size"), population=("w_person", "sum"))
                .assign(sample_share=lambda x: 100 * x.sample_households / x.sample_households.sum(),
                        population_share=lambda x: 100 * x.population / x.population.sum())
                .assign(sampling_ratio=lambda x: x.sample_share / x.population_share)
                .sort_values("sampling_ratio", ascending=False))
by_domain[["sample_households", "sample_share", "population_share", "sampling_ratio"]].round(2)
""")

code("""
rural = hog["clase"] == 2
print(f"Rural: {100*rural.mean():.1f}% of sampled households, "
      f"{100*hog.loc[rural, 'w_person'].sum()/hog['w_person'].sum():.1f}% of the population")
""")

md("## 3. Chart")

code("""
fig, ax = plt.subplots(figsize=(8, 3.6))
labels = ["Unweighted\\nhouseholds", "Weighted\\nhouseholds", "Unweighted\\npersons", "Weighted\\npersons"]
colors = ["#b0b0b0", "#b0b0b0", "#b0b0b0", "#1f5fa8"]
bars = ax.bar(labels, methods["rate"], color=colors, width=0.6)
ax.axhline(official.POVERTY[(YEAR, "nacional")], color="#c0392b", lw=1.2, ls="--")
ax.text(-0.45, official.POVERTY[(YEAR, "nacional")] + 0.5, "DANE official: 28.0%", color="#c0392b",
        ha="left", fontsize=9)
for b, v in zip(bars, methods["rate"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}%", ha="center", fontsize=10)
ax.set_ylabel("Poverty incidence (%)")
ax.set_ylim(0, max(methods["rate"]) + 4)
ax.set_title("Colombia 2025: same microdata, four estimates of the poverty rate", fontsize=11, loc="left")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIGS / "weights_comparison_2025.png", dpi=200)
plt.show()
""")

md("""
## 4. Notes for the write-up

- All nine figures (poverty, extreme poverty, Gini × national/urban/rural) round to DANE's
  published values.
- **Getting the unit exactly right mattered.** Weighting households by persons in the spending
  unit (`npersug`) gives 28.05% poverty, 9.65% extreme poverty (rounds to 9.7, not DANE's 9.6) and a
  Gini 0.001–0.002 too low. Weighting by all household members (`nper`) — each assigned the
  spending unit's per-capita income — reproduces every published figure.
""")

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python (povcol)", "language": "python", "name": "povcol"},
                                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"c{i:02d}"
out = Path(__file__).with_name("02_replicate.ipynb")
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
print("wrote", out)
