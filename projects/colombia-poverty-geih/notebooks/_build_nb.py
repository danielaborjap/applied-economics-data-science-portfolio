"""Builds 01_load_data.ipynb (kept so the notebook is reproducible from source)."""
import json
from pathlib import Path

cells = []


def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})


def code(s):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": s.strip("\n")})


md("""
# 01 · Load DANE's monetary-poverty microdata

**Goal of this notebook:** load the `hogares` and `personas` files of *Medición de Pobreza
Monetaria y Desigualdad* for one year, map the variable names, and run sanity checks
before any estimation. Replication of the official rates happens in `02_replicate.ipynb`.

Get the data first: `python data/download.py 2025 --zip <file>` (see `data/download.py`).
""")

code("""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

from povcol.load import load, HH_KEYS
from povcol.weighted import weighted_rate

YEAR = 2025
APPLY_SPLICE = False   # True only for the *empalme* datasets (ingpcug * fac_emp)
""")

md("## 1. Load and map variable names\nCheck the printed mapping against the data dictionary for this year.")

code("""
hog = load(YEAR, "hogares", apply_splice=APPLY_SPLICE)
per = load(YEAR, "personas")

print("hogares:", hog.shape, "\\npersonas:", per.shape)
print("\\nColumn mapping used (standard -> original):")
for name, df in [("hogares", hog), ("personas", per)]:
    print(f"  {name}: {df.attrs['column_map']}")
""")

code("""
needed = ["fex", "ingpcug", "lp", "li", "pobre", "indigente", "npersug", "nper", "clase", "dpto"]
missing = [c for c in needed if c not in hog.columns]
print("Missing in hogares:", missing or "none")
hog[[c for c in needed if c in hog.columns]].describe().T
""")

md("## 2. Sanity checks")

code("""
# Keys: one row per household
dups = hog.duplicated(HH_KEYS).sum()
print(f"Duplicate household keys: {dups}")

# Expansion factors should sum to ~ number of households;
# fex * persons in spending unit should sum to ~ national population (~53 million)
print(f"Sum fex (households):            {hog['fex'].sum():,.0f}")
print(f"Sum fex*nper (all persons):      {(hog['fex'] * hog['nper']).sum():,.0f}")
print(f"Sum fex*npersug (persons in UG): {(hog['fex'] * hog['npersug']).sum():,.0f}")
if "fex" in per.columns:
    print(f"Sum fex over personas file:      {per['fex'].sum():,.0f}")
""")

code("""
# Poverty flags should agree with income vs. lines
chk = pd.DataFrame({
    "pobre_flag": hog["pobre"],
    "pobre_recomputed": (hog["ingpcug"] < hog["lp"]).astype(int),
    "indig_flag": hog["indigente"],
    "indig_recomputed": (hog["ingpcug"] < hog["li"]).astype(int),
})
print("pobre flag == (ingpcug < lp):     ", (chk.pobre_flag == chk.pobre_recomputed).mean())
print("indigente flag == (ingpcug < li): ", (chk.indig_flag == chk.indig_recomputed).mean())
print("\\nLines vary by domain; national per-capita lines in the bulletin: lp=482,041, li=236,580")
hog[["lp", "li"]].drop_duplicates().describe()
""")

md("""
## 3. First look (preliminary, not the replication)

Poverty incidence is a share of **persons**, but `hogares` has one row per household.
So each household is weighted by `fex × nper` (all persons in the household; each is assigned
the spending unit's per-capita income).
""")

code("""
w_person = hog["fex"] * hog["nper"]
print(f"Weighted (persons):   {weighted_rate(hog['pobre'], w_person):.2f}%   official 28.0%")
print(f"Weighted (households):{weighted_rate(hog['pobre'], hog['fex']):.2f}%")
print(f"Unweighted rows:      {weighted_rate(hog['pobre']):.2f}%")
""")

md("Next: `02_replicate.ipynb` — full replication table, extreme poverty, and the weighted vs unweighted comparison.")

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"c{i:02d}"
out = Path(__file__).with_name("01_load_data.ipynb")
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
print("wrote", out)
