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


# Departmental monetary poverty (%), DANE press release "Pobreza monetaria departamental 2025"
# https://www.dane.gov.co/files/operaciones/PM/cp-PMDepartamental-2025.pdf
DEPT_POVERTY = {
    "Chocó": (67.4, 65.3), "La Guajira": (65.7, 60.2), "Sucre": (57.5, 51.8),
    "Magdalena": (51.7, 46.5), "Bolívar": (48.0, 44.8), "Cesar": (47.8, 44.4),
    "Córdoba": (49.6, 44.0), "Cauca": (43.1, 40.9), "Huila": (40.4, 39.8),
    "Caquetá": (37.4, 34.9), "Norte de Santander": (35.3, 33.7), "Nariño": (39.2, 33.4),
    "Boyacá": (30.9, 31.6), "Tolima": (35.6, 28.0), "Atlántico": (31.6, 27.3),
    "Santander": (27.4, 24.0), "Meta": (23.6, 22.1), "Valle del Cauca": (25.7, 21.8),
    "Quindío": (25.9, 20.9), "Risaralda": (23.8, 20.2), "Antioquia": (24.7, 19.2),
    "Bogotá D.C.": (19.6, 17.8), "Caldas": (20.0, 17.5), "Cundinamarca": (20.1, 15.1),
}  # (2024, 2025)

# Poverty by sex, national 2025, DANE "Pobreza monetaria con enfoque diferencial 2025"
# https://www.dane.gov.co/files/operaciones/PM/bol-PMEnfoqueDiferencial-2025.pdf
SEX_2025 = {
    ("poverty", "head", "man"): 24.5, ("poverty", "head", "woman"): 32.3,
    ("poverty", "population", "man"): 26.8, ("poverty", "population", "woman"): 29.1,
    ("extreme", "head", "man"): 8.0, ("extreme", "head", "woman"): 11.7,
    ("extreme", "population", "man"): 9.2, ("extreme", "population", "woman"): 10.1,
}
