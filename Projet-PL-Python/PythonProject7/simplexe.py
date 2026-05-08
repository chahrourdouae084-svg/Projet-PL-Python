from calculs import (
    NOMS_4VAR,
    NOMS_CONTRAINTES_4VAR,
    resoudre_simplexe,
    verifier_utilisation_ressources,
    A_CONTRAINTES_4VAR,
    B_CONTRAINTES_4VAR,
    OBJECTIF_4VAR,
)


def afficher_formulation():
    print("=" * 65)
    print("  PROBLEME DE PL - 4 MEDICAMENTS")
    print("=" * 65)
    print()
    print("  Variables :")
    for i, nom in enumerate(NOMS_4VAR, 1):
        print(f"    x{i} = {nom}")
    print()
    c = [-v for v in OBJECTIF_4VAR]
    expr = " + ".join(f"{c[i]}x{i+1}" for i in range(len(c)))
    print(f"  Max Z = {expr}")
    print()
    print("  Contraintes :")
    for i, (ligne, lim) in enumerate(zip(A_CONTRAINTES_4VAR, B_CONTRAINTES_4VAR)):
        termes = [f"{coef}x{j+1}" for j, coef in enumerate(ligne) if coef != 0]
        print(f"    [{i+1}] {' + '.join(termes)} <= {lim}")
    print()
    print("  x1, x2, x3, x4 >= 0")
    print()


def afficher_resultats(sol):
    print("=" * 65)
    print("  RESULTATS - SIMPLEXE")
    print("=" * 65)

    if not sol["succes"]:
        print(f"  Echec : {sol['message']}")
        return

    print("\n  Solution trouvee :\n")
    for i, (nom, val) in enumerate(zip(sol["noms"], sol["variables"]), 1):
        print(f"    x{i} ({nom}) = {val}")

    print(f"\n  Z = {sol['profit_max']}\n")

    print("=" * 65)
    print("  RESSOURCES")
    print("=" * 65)
    for r in verifier_utilisation_ressources(sol["variables"]):
        pct    = r["utilisation"] / r["limite"] * 100
        statut = "SATUREE" if r["saturee"] else "ok"
        print(f"\n  {r['nom']}")
        print(f"    {r['utilisation']} / {r['limite']}  ({pct:.1f}%)  -> {statut}")

    print()
    print("  Contraintes saturees :")
    if sol["contraintes_saturees"]:
        for s in sol["contraintes_saturees"]:
            print(f"    * {s}")
    else:
        print("    aucune")
    print()


def exporter_resultats(sol, chemin="resultats_simplexe.txt"):
    if not sol["succes"]:
        return

    rapport = verifier_utilisation_ressources(sol["variables"])
    lignes  = [
        "=" * 65,
        "  RESULTATS - SIMPLEXE",
        "  Stocks de medicaments",
        "=" * 65, "",
        "  Variables :",
    ]
    for i, (nom, val) in enumerate(zip(sol["noms"], sol["variables"]), 1):
        lignes.append(f"    x{i} ({nom}) = {val}")
    lignes += ["", f"  Z = {sol['profit_max']}", "", "  Ressources :"]
    for r in rapport:
        s = "SATUREE" if r["saturee"] else "ok"
        lignes.append(
            f"    {r['nom']} : {r['utilisation']} / {r['limite']}"
            f" | marge={r['marge']} | {s}"
        )
    lignes += ["", "=" * 65]

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))
    print(f"Exporte -> {chemin}")


if __name__ == "__main__":
    afficher_formulation()
    sol = resoudre_simplexe()
    afficher_resultats(sol)
    exporter_resultats(sol)