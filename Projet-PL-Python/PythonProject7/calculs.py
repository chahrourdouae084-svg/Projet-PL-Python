import numpy as np
from scipy.optimize import linprog

# Z = 2x1 + 3x2
COEFF_OBJECTIF = [2, 3]

CONTRAINTES_2VAR = {
    "Budget"     : ([5, 8], 500),
    "Stockage"   : ([1, 1], 100),
    "Paracetamol": ([1, 0], 80),
    "Doliprane"  : ([0, 1], 60),
}

NOMS_2VAR = ["Paracetamol (x1)", "Doliprane (x2)"]


def calculer_intersection(a1, b1, c1, a2, b2, c2):
    D  = a1*b2 - a2*b1
    Dx = c1*b2 - c2*b1
    Dy = a1*c2 - a2*c1
    if abs(D) < 1e-10:
        return None
    return (round(Dx/D, 4), round(Dy/D, 4))


def point_est_realisable(x, y, contraintes=CONTRAINTES_2VAR, tol=1e-6):
    if x < -tol or y < -tol:
        return False
    for nom, (coeffs, limite) in contraintes.items():
        if coeffs[0]*x + coeffs[1]*y > limite + tol:
            return False
    return True


def trouver_sommets(contraintes=CONTRAINTES_2VAR):
    droites = []
    for nom, (coeffs, limite) in contraintes.items():
        droites.append((coeffs[0], coeffs[1], limite, nom))
    droites.append((1, 0, 0, "x=0"))
    droites.append((0, 1, 0, "y=0"))

    sommets = []
    n = len(droites)

    for i in range(n):
        for j in range(i+1, n):
            a1, b1, c1, _ = droites[i]
            a2, b2, c2, _ = droites[j]
            pt = calculer_intersection(a1, b1, c1, a2, b2, c2)
            if pt is None:
                continue
            x, y = pt
            if not point_est_realisable(x, y):
                continue
            deja_la = any(abs(x-sx) < 1e-4 and abs(y-sy) < 1e-4
                         for sx, sy in sommets)
            if not deja_la:
                sommets.append((x, y))

    return sommets


def evaluer_objectif(x, y, coeffs=COEFF_OBJECTIF):
    return coeffs[0]*x + coeffs[1]*y


def trouver_solution_optimale_graphique():
    sommets   = trouver_sommets()
    resultats = []
    best_z    = -1e9
    best_pt   = None

    for x, y in sommets:
        z = evaluer_objectif(x, y)
        resultats.append((x, y, z))
        if z > best_z:
            best_z  = z
            best_pt = (x, y)

    resultats.sort(key=lambda t: t[2], reverse=True)

    return {
        "sommets"      : resultats,
        "optimal_x"   : best_pt[0] if best_pt else None,
        "optimal_y"   : best_pt[1] if best_pt else None,
        "profit_max"  : best_z,
        "point_optimal": best_pt,
    }


NOMS_4VAR = ["Paracetamol", "Doliprane", "Ibuprofene", "Amoxicilline"]

OBJECTIF_4VAR = [-2, -3, -4, -5]

A_CONTRAINTES_4VAR = [
    [5, 8, 6, 10],
    [1, 1, 1,  1],
    [1, 0, 0,  0],
    [0, 1, 0,  0],
    [0, 0, 1,  0],
    [0, 0, 0,  1],
]

B_CONTRAINTES_4VAR = [800, 150, 80, 60, 50, 40]
BORNES_4VAR        = [(0, None)] * 4

NOMS_CONTRAINTES_4VAR = [
    "Budget (5x1+8x2+6x3+10x4 <= 800)",
    "Stockage (x1+x2+x3+x4 <= 150)",
    "Demande Paracetamol (x1 <= 80)",
    "Demande Doliprane (x2 <= 60)",
    "Demande Ibuprofene (x3 <= 50)",
    "Demande Amoxicilline (x4 <= 40)",
]


def resoudre_simplexe():
    res = linprog(
        c      = OBJECTIF_4VAR,
        A_ub   = A_CONTRAINTES_4VAR,
        b_ub   = B_CONTRAINTES_4VAR,
        bounds = BORNES_4VAR,
        method = "highs"
    )

    if not res.success:
        return {"succes": False, "message": res.message}

    vars_opt   = [round(v, 4) for v in res.x]
    profit_max = round(-res.fun, 4)

    saturees = []
    for i, (ligne, limite) in enumerate(zip(A_CONTRAINTES_4VAR, B_CONTRAINTES_4VAR)):
        val = sum(ligne[j]*vars_opt[j] for j in range(4))
        if abs(limite - val) < 1e-4:
            saturees.append(NOMS_CONTRAINTES_4VAR[i])

    return {
        "succes"              : True,
        "variables"           : vars_opt,
        "profit_max"          : profit_max,
        "contraintes_saturees": saturees,
        "message"             : res.message,
        "noms"                : NOMS_4VAR,
    }


def verifier_utilisation_ressources(variables):
    rapport = []
    for i, (ligne, limite) in enumerate(zip(A_CONTRAINTES_4VAR, B_CONTRAINTES_4VAR)):
        val   = sum(ligne[j]*variables[j] for j in range(4))
        marge = limite - val
        rapport.append({
            "nom"        : NOMS_CONTRAINTES_4VAR[i],
            "utilisation": round(val, 4),
            "limite"     : limite,
            "marge"      : round(marge, 4),
            "saturee"    : abs(marge) < 1e-4,
        })
    return rapport