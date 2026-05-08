import sys


def verifier_dependances():
    for module in ["numpy", "scipy", "matplotlib"]:
        try:
            __import__(module)
        except ImportError:
            print(f"Module manquant : {module}")
            print("Installez avec : pip install numpy scipy matplotlib")
            sys.exit(1)


def afficher_banniere():
    print()
    print("=" * 65)
    print("   OPTIMISATION DES STOCKS DE MEDICAMENTS")
    print("=" * 65)
    print()


def lancer_calculs_terminal():
    from calculs import trouver_solution_optimale_graphique, resoudre_simplexe
    from simplexe import afficher_formulation, afficher_resultats

    print("=" * 65)
    print("  PARTIE 1 - METHODE GRAPHIQUE")
    print("=" * 65)
    print()
    print("  Max Z = 2x1 + 3x2")
    print("  5x1+8x2<=500  |  x1+x2<=100  |  x1<=80  |  x2<=60")
    print()

    sol = trouver_solution_optimale_graphique()
    pts = ["D", "E", "A", "B", "C"]

    print(f"  {'Pt':<5}  {'x1':>8}  {'x2':>8}  {'Z':>10}")
    print("  " + "-" * 36)

    for i, (x, y, z) in enumerate(sol["sommets"]):
        opt = (
            abs(x - sol["optimal_x"]) < 1e-4 and
            abs(y - sol["optimal_y"]) < 1e-4
        )

        mk = " <- OPTIMAL" if opt else ""
        nom = pts[i] if i < len(pts) else f"S{i}"

        print(f"  {nom:<5}  {x:>8.2f}  {y:>8.2f}  {z:>10.2f}{mk}")

    print()
    print(f"  x1={sol['optimal_x']}  x2={sol['optimal_y']}  Z={sol['profit_max']}")
    print()

    afficher_formulation()
    afficher_resultats(resoudre_simplexe())


def lancer_interface():
    print("Lancement de l'interface ...")

    from interface import ApplicationPL

    app = ApplicationPL()
    app.mainloop()


if __name__ == "__main__":
    verifier_dependances()
    afficher_banniere()
    lancer_calculs_terminal()
    print()
    lancer_interface()