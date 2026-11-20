"""Official DANE figures to replicate.

Source: DANE, Boletín técnico "Pobreza monetaria en Colombia, Año 2025"
(12 June 2026), https://www.dane.gov.co/files/operaciones/PM/bol-PM-2025.pdf
Incidence in % of persons; Gini on per-capita income of the spending unit.
"""

POVERTY = {  # (year, domain): incidence %
    (2024, "nacional"): 31.8, (2025, "nacional"): 28.0,
    (2024, "cabeceras"): 28.6, (2025, "cabeceras"): 24.6,
    (2024, "rural"): 42.5, (2025, "rural"): 39.5,
}

EXTREME = {
    (2024, "nacional"): 11.7, (2025, "nacional"): 9.6,
    (2024, "cabeceras"): 8.7, (2025, "cabeceras"): 6.9,
    (2024, "rural"): 21.8, (2025, "rural"): 19.1,
}

GINI = {
    (2024, "nacional"): 0.551, (2025, "nacional"): 0.531,
    (2024, "cabeceras"): 0.530, (2025, "cabeceras"): 0.507,
    (2024, "rural"): 0.482, (2025, "rural"): 0.476,
}

# National per-capita monthly lines, 2025, COP
LINES_2025 = {"lp": 482_041, "li": 236_580}
