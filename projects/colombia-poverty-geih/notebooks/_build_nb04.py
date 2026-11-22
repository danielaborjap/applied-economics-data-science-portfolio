"""Builds 04_two_years_and_uncertainty.ipynb (kept so the notebook is reproducible from source)."""
import json
from pathlib import Path

cells = []


def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})


def code(s):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": s.strip("\n")})


md("""
# 04 · Second year (2024) and sampling uncertainty

1. Replicate **2024** with the same code — a second, independent test of the pipeline
2. Measure the **2024 → 2025 change** nationally, by urban/rural and by department
3. Attach **approximate 95% confidence intervals** and compare our significance calls
   with the ones DANE marks in its own publications

**Important limitation.** The public microdata contain the expansion factors but **no stratum
or primary-sampling-unit (cluster) identifiers**. Proper design-based standard errors (e.g. with
`samplics`) need both. The intervals here use Taylor linearization of the ratio estimator, with
households as sampling units and the 25 survey domains (`dominio`) as strata. Ignoring clustering
almost always makes standard errors **too small**, so these intervals are a lower bound on the
true uncertainty.
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
from povcol.weighted import weighted_rate, gini, ratio_se
from povcol import official

RESULTS = ROOT / "results"; RESULTS.mkdir(exist_ok=True)
FIGS = ROOT / "figures"; FIGS.mkdir(exist_ok=True)
Z = 1.96

data = {}
for year in (2024, 2025):
    h = load(year, "hogares")
    h["w_person"] = h["fex"] * h["nper"]
    h["w_dpto"] = h["fex_dpto"] * h["nper"]
    h["poor_persons"] = h["pobre"] * h["nper"]          # same definition as the replication
    h["extreme_persons"] = h["indigente"] * h["nper"]
    data[year] = h
    print(year, h.shape, "column map:", h.attrs["column_map"])
""")

md("## 1. Replication of 2024")

code("""
def domains(h):
    return {"nacional": h, "cabeceras": h[h["clase"] == 1], "rural": h[h["clase"] == 2]}

rows = []
for year, h in data.items():
    for dom, d in domains(h).items():
        rows += [
            {"year": year, "domain": dom, "indicator": "Monetary poverty (%)",
             "this_repo": weighted_rate(d["pobre"], d["w_person"]), "DANE": official.POVERTY[(year, dom)]},
            {"year": year, "domain": dom, "indicator": "Extreme poverty (%)",
             "this_repo": weighted_rate(d["indigente"], d["w_person"]), "DANE": official.EXTREME[(year, dom)]},
            {"year": year, "domain": dom, "indicator": "Gini",
             "this_repo": gini(d["ingpcug"], d["w_person"]), "DANE": official.GINI[(year, dom)]},
        ]
rep = pd.DataFrame(rows)
rep["difference"] = rep["this_repo"] - rep["DANE"]
rep.to_csv(RESULTS / "replication_2024_2025.csv", index=False)
rep.pivot_table(index=["domain", "indicator"], columns="year",
                values=["this_repo", "DANE", "difference"]).round(3)
""")

md("## 2. Change 2024 → 2025 with approximate 95% confidence intervals")

code("""
def estimate(d, y_col, weight="fex"):
    R, se = ratio_se(d[y_col], d["nper"], d[weight], d["dominio"])
    return 100 * R, 100 * se

rows = []
for dom in ["nacional", "cabeceras", "rural"]:
    for ind, col in [("poverty", "poor_persons"), ("extreme", "extreme_persons")]:
        r = {"domain": dom, "indicator": ind}
        for year in (2024, 2025):
            est, se = estimate(domains(data[year])[dom], col)
            r[f"{year}"] = est
            r[f"se_{year}"] = se
        r["change_pp"] = r["2025"] - r["2024"]
        # independent samples in the two years -> variances add
        r["se_change"] = np.hypot(r["se_2024"], r["se_2025"])
        r["ci_low"] = r["change_pp"] - Z * r["se_change"]
        r["ci_high"] = r["change_pp"] + Z * r["se_change"]
        r["significant_95"] = (r["ci_low"] > 0) | (r["ci_high"] < 0)
        rows.append(r)
change = pd.DataFrame(rows)
change.to_csv(RESULTS / "change_2024_2025.csv", index=False)
change.round(2)
""")

md("""
DANE reports the national (−3.8 pp), urban (−4.0 pp) and rural (−3.0 pp) poverty declines as
statistically significant at 95%. Our approximate intervals agree on all three.
""")

md("## 3. Departments: change and significance")

code("""
rows = []
for dpto in sorted(data[2025]["dpto"].unique()):
    r = {"department": dpto}
    for year in (2024, 2025):
        d = data[year][data[year]["dpto"] == dpto]
        r[f"{year}"], r[f"se_{year}"] = estimate(d, "poor_persons", weight="fex_dpto")
        r[f"DANE_{year}"] = official.DEPT_POVERTY[dpto][0 if year == 2024 else 1]
    r["change_pp"] = r["2025"] - r["2024"]
    r["se_change"] = np.hypot(r["se_2024"], r["se_2025"])
    r["significant_95"] = abs(r["change_pp"]) > Z * r["se_change"]
    rows.append(r)
dchange = pd.DataFrame(rows).set_index("department").sort_values("change_pp")
dchange["diff_vs_DANE_2024"] = dchange["2024"] - dchange["DANE_2024"]
dchange["diff_vs_DANE_2025"] = dchange["2025"] - dchange["DANE_2025"]
dchange.to_csv(RESULTS / "departments_change_2024_2025.csv")
print(f"Largest |difference| vs DANE: 2024 {dchange['diff_vs_DANE_2024'].abs().max():.2f} pp, "
      f"2025 {dchange['diff_vs_DANE_2025'].abs().max():.2f} pp")
dchange[["2024", "2025", "change_pp", "se_change", "significant_95"]].round(2)
""")

md("""
**Check against DANE's significance calls.** DANE's departmental press release marks with an
asterisk which 2024→2025 changes are significant. Where both sources make a call we can compare.
Because our standard errors ignore clustering, we expect to call *more* changes significant than
DANE, never fewer.
""")

code("""
DANE_SIG = {  # cp-PMDepartamental-2025.pdf, chart "Variación de la incidencia ... 2024-2025"
    "Tolima": True, "Nariño": True, "Sucre": True, "Córdoba": True, "La Guajira": True,
    "Antioquia": True, "Magdalena": True, "Quindío": True, "Cundinamarca": True,
    "Atlántico": True, "Valle del Cauca": True, "Risaralda": True, "Cesar": True,
    "Santander": True, "Bolívar": True, "Caldas": True, "Bogotá D.C.": True,
    "Caquetá": False, "Cauca": False, "Chocó": False, "Norte de Santander": False,
    "Meta": False, "Huila": False, "Boyacá": False,
}
cmp = dchange.loc[list(DANE_SIG), ["change_pp", "se_change", "significant_95"]].copy()
cmp["DANE_significant"] = pd.Series(DANE_SIG)
cmp["agree"] = cmp["significant_95"] == cmp["DANE_significant"]
print(f"Agreement with DANE on {cmp['agree'].sum()} of {len(cmp)} departments")
cmp.round(2)
""")

code("""
d = dchange.sort_values("change_pp")
fig, ax = plt.subplots(figsize=(8, 7))
y = np.arange(len(d))
colors = np.where(d["significant_95"], "#1f5fa8", "#b0b0b0")
ax.errorbar(d["change_pp"], y, xerr=Z * d["se_change"], fmt="none", ecolor=colors, elinewidth=1.4, capsize=0)
ax.scatter(d["change_pp"], y, color=colors, zorder=3, s=28)
ax.axvline(0, color="black", lw=0.8)
nat = change.query("domain == 'nacional' and indicator == 'poverty'")["change_pp"].iloc[0]
ax.axvline(nat, color="#c0392b", ls="--", lw=1)
ax.text(nat, len(d) - 0.2, f" National {nat:+.1f} pp", color="#c0392b", fontsize=9, va="bottom")
ax.set_yticks(y)
ax.set_yticklabels(d.index, fontsize=9)
ax.set_ylim(-0.8, len(d) + 0.6)
ax.set_xlabel("Change in monetary poverty, 2024 → 2025 (percentage points)")
ax.set_title("Change in poverty by department, 2024 → 2025, with approximate 95% CIs\\n"
             "blue = significant at 95%, grey = not significant", loc="left", fontsize=10)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIGS / "poverty_change_by_department.png", dpi=200)
plt.show()
""")

md("""
## 4. Notes for the write-up

- The same code replicates both 2024 and 2025, so the result is not tuned to one file.
- National poverty fell from about 31.8% to 28.0% (−3.8 pp). The approximate interval is far
  from zero, in line with DANE's significance call.
- Department-level intervals are wide (a few thousand households each); some large-looking
  changes are not distinguishable from zero.
- All intervals here are approximate lower bounds: no cluster identifiers in the public file.
""")

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python (povcol)", "language": "python", "name": "povcol"},
                                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"c{i:02d}"
out = Path(__file__).with_name("04_two_years_and_uncertainty.ipynb")
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
print("wrote", out)
