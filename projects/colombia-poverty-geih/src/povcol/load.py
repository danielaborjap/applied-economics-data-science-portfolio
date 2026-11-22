"""Load DANE's "Medición de Pobreza Monetaria y Desigualdad" microdata.

The dataset ships two files, `hogares` and `personas` (CSV, SAV or DTA,
depending on the release). Variable names change between years, so this
module lower-cases everything and maps known aliases to standard names.
ALWAYS confirm the mapping against the data dictionary of the year you use.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"

# standard name -> candidate column names (lower-case), first match wins
ALIASES = {
    "directorio": ["directorio"],
    "secuencia_p": ["secuencia_p"],
    "orden": ["orden"],
    "clase": ["clase"],            # 1 = cabecera (urban), 2 = centros poblados y rural disperso
    "dpto": ["dpto", "depto", "departamento"],
    "dominio": ["dominio"],
    "fex": ["fex_c", "fex_c18", "fex_c_2011", "fex"],   # expansion factor (annualized), national/urban-rural
    "fex_dpto": ["fex_dpto"],      # departmental expansion factor: use for department-level estimates
    "npobres": ["npobres"],        # number of poor persons in the household
    "nindigentes": ["nindigentes"],
    "fac_emp": ["fac_emp"],        # splice factor, empalme datasets only
    "ingpcug": ["ingpcug"],        # per-capita income of the spending unit
    "lp": ["lp"],                  # poverty line (per capita, monthly)
    "li": ["li"],                  # extreme poverty line
    "pobre": ["pobre"],
    "indigente": ["indigente"],
    "npersug": ["npersug"],        # persons in the spending unit
    "nper": ["nper"],
    "sexo": ["p6020", "p3271"],    # 1 = man, 2 = woman
    "edad": ["p6040"],
    "parentesco": ["p6050"],       # 1 = household head
}

HH_KEYS = ["directorio", "secuencia_p"]

# DIVIPOLA department codes. The 2024 file stores dpto as codes ("05"), 2025 as names.
DPTO_NAMES = {
    5: "Antioquia", 8: "Atlántico", 11: "Bogotá D.C.", 13: "Bolívar", 15: "Boyacá",
    17: "Caldas", 18: "Caquetá", 19: "Cauca", 20: "Cesar", 23: "Córdoba",
    25: "Cundinamarca", 27: "Chocó", 41: "Huila", 44: "La Guajira", 47: "Magdalena",
    50: "Meta", 52: "Nariño", 54: "Norte de Santander", 63: "Quindío", 66: "Risaralda",
    68: "Santander", 70: "Sucre", 73: "Tolima", 76: "Valle del Cauca",
}

# Columns that must be numeric. Some releases store codes as text (e.g. clase = "1" in 2024),
# which would silently break comparisons like clase == 1.
NUMERIC = ["directorio", "secuencia_p", "orden", "clase", "fex", "fex_dpto", "fac_emp",
           "ingpcug", "lp", "li", "pobre", "indigente", "npobres", "nindigentes",
           "npersug", "nper", "sexo", "edad", "parentesco"]


def _find(raw_dir: Path, stem: str) -> Path:
    hits = [p for p in raw_dir.rglob("*")
            if p.is_file() and stem in p.stem.lower()
            and p.suffix.lower() in {".csv", ".sav", ".dta", ".parquet"}]
    if not hits:
        raise FileNotFoundError(
            f"No '{stem}' file under {raw_dir}. Run `python data/download.py` first.")
    # prefer parquet > dta > sav > csv (faster / typed)
    rank = {".parquet": 0, ".dta": 1, ".sav": 2, ".csv": 3}
    return sorted(hits, key=lambda p: rank[p.suffix.lower()])[0]


def _read(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(path, columns=columns)
    if suf == ".dta":
        return pd.read_stata(path, columns=columns, convert_categoricals=False)
    if suf == ".sav":
        return pd.read_spss(path, usecols=columns, convert_categoricals=False)
    # DANE CSVs are usually ';'-separated with ',' decimals; sniff the separator
    with open(path, encoding="latin-1") as fh:
        head = fh.readline()
    sep = ";" if head.count(";") > head.count(",") else ","
    dec = "," if sep == ";" else "."
    if columns is not None:
        wanted = {c.lower() for c in columns}
        return pd.read_csv(path, sep=sep, decimal=dec, encoding="latin-1", low_memory=False,
                           usecols=lambda c: c.lower() in wanted)
    return pd.read_csv(path, sep=sep, decimal=dec, encoding="latin-1", low_memory=False)


def standardize(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Lower-case columns and rename known aliases. Returns (df, mapping_used)."""
    df = df.rename(columns=str.lower)
    used = {}
    for std, cands in ALIASES.items():
        for c in cands:
            if c in df.columns:
                used[std] = c
                break
    df = df.rename(columns={v: k for k, v in used.items()})
    for c in NUMERIC:
        if c in df.columns and not pd.api.types.is_numeric_dtype(df[c]):
            df[c] = pd.to_numeric(df[c].astype(str).str.strip().str.replace(",", ".", regex=False),
                                  errors="raise")
    if "dpto" in df.columns:
        codes = pd.to_numeric(df["dpto"], errors="coerce")
        if codes.notna().all():
            df["dpto"] = codes.astype(int).map(DPTO_NAMES)
            if df["dpto"].isna().any():
                raise ValueError("unknown department code")
    return df, used


def load(year: int, which: str = "hogares", raw_dir: Path | None = None,
         apply_splice: bool = False, columns: list[str] | None = None) -> pd.DataFrame:
    """Load one file ('hogares' or 'personas') for `year` from data/raw/<year>/.

    apply_splice: multiply ingpcug by fac_emp (only for the empalme datasets,
    per DANE's note, to compare with GEIH marco-2018 publications).
    columns: original (file) column names to read, e.g. to load only part of `personas`.
    """
    raw_dir = raw_dir or RAW / str(year)
    df, used = standardize(_read(_find(raw_dir, which), columns))
    df.attrs["column_map"] = used
    if apply_splice:
        if "fac_emp" not in df.columns:
            raise KeyError("apply_splice=True but no fac_emp column in this file")
        df["ingpcug"] = df["ingpcug"] * df["fac_emp"]
    return df


def household_head_sex(personas: pd.DataFrame) -> pd.DataFrame:
    """One row per household with the sex of its head (parentesco == 1)."""
    heads = personas.loc[personas["parentesco"] == 1, HH_KEYS + ["sexo"]]
    heads = heads.drop_duplicates(HH_KEYS).rename(columns={"sexo": "sexo_jefe"})
    return heads
