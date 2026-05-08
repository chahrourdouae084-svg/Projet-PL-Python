import numpy as np
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib.lines import Line2D

from calculs import (
    CONTRAINTES_2VAR,
    COEFF_OBJECTIF,
    trouver_solution_optimale_graphique,
)

COULEUR_REGION = "#c8e6c9"
COULEUR_OPTIMAL = "#e53935"
COULEUR_SOMMETS = "#1565c0"

COULEURS_DROITES = [
    "#6a1b9a",
    "#0277bd",
    "#2e7d32",
    "#e65100",
]


def tracer_surface_realisable(save_path=None):
    sol = trouver_solution_optimale_graphique()

    x_opt = sol["optimal_x"]
    y_opt = sol["optimal_y"]
    z_max = sol["profit_max"]

    xmax = 120
    ymax = 100

    xs = np.linspace(0, xmax, 500)
    ys = np.linspace(0, ymax, 500)

    X, Y = np.meshgrid(xs, ys)

    masque = (X >= 0) & (Y >= 0)

    for nom, (coeffs, limite) in CONTRAINTES_2VAR.items():
        masque &= (coeffs[0] * X + coeffs[1] * Y <= limite)

    fig, ax = plt.subplots(figsize=(11, 8))

    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")

    ax.contourf(
        X,
        Y,
        masque.astype(float),
        levels=[0.5, 1.5],
        colors=[COULEUR_REGION],
        alpha=0.6,
        zorder=1
    )

    ax.contour(
        X,
        Y,
        masque.astype(float),
        levels=[0.5],
        colors=["#388e3c"],
        linewidths=1.5,
        linestyles="--",
        zorder=2
    )

    x_line = np.linspace(0, xmax, 400)

    for idx, (nom, (coeffs, limite)) in enumerate(CONTRAINTES_2VAR.items()):

        a, b = coeffs
        couleur = COULEURS_DROITES[idx % len(COULEURS_DROITES)]

        if abs(b) > 1e-10:

            y_line = (limite - a * x_line) / b

            ok = (
                (y_line >= 0) &
                (y_line <= ymax) &
                (x_line >= 0)
            )

            if ok.any():

                ax.plot(
                    x_line[ok],
                    y_line[ok],
                    color=couleur,
                    linewidth=2,
                    label=f"{nom} : {a}x1+{b}x2<={limite}",
                    zorder=3
                )

        else:

            xv = limite / a

            ax.axvline(
                x=xv,
                color=couleur,
                linewidth=2,
                label=f"{nom} : x1<={limite}",
                zorder=3
            )

    for sx, sy, sz in sol["sommets"]:

        est_opt = (
            abs(sx - x_opt) < 1e-4 and
            abs(sy - y_opt) < 1e-4
        )

        if est_opt:

            ax.scatter(
                sx,
                sy,
                color=COULEUR_OPTIMAL,
                s=160,
                zorder=6,
                edgecolors="black",
                linewidths=1.5
            )

            ax.annotate(
                f"Optimal ({sx}, {sy})\nZ={sz}",
                xy=(sx, sy),
                fontsize=10,
                fontweight="bold",
                color=COULEUR_OPTIMAL
            )

        else:

            ax.scatter(
                sx,
                sy,
                color=COULEUR_SOMMETS,
                s=80,
                zorder=5,
                edgecolors="black",
                linewidths=1
            )

    y_obj = (
        z_max - COEFF_OBJECTIF[0] * x_line
    ) / COEFF_OBJECTIF[1]

    ok2 = (
        (y_obj >= 0) &
        (y_obj <= ymax) &
        (x_line >= 0)
    )

    if ok2.any():

        ax.plot(
            x_line[ok2],
            y_obj[ok2],
            color=COULEUR_OPTIMAL,
            linewidth=2.5,
            linestyle="dashdot",
            label=f"Z={COEFF_OBJECTIF[0]}x1+{COEFF_OBJECTIF[1]}x2={z_max}",
            zorder=4
        )

    ax.set_xlim(-3, xmax)
    ax.set_ylim(-3, ymax)

    ax.set_xlabel("x1 (Paracetamol)")
    ax.set_ylabel("x2 (Doliprane)")

    ax.set_title(
        "Region realisable — Gestion des stocks de medicaments"
    )

    ax.grid(True, linestyle="--", alpha=0.4)

    region_patch = mpatches.Patch(
        facecolor=COULEUR_REGION,
        edgecolor="#388e3c",
        label="Region realisable"
    )

    sommet_pt = Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=COULEUR_SOMMETS,
        markersize=9,
        label="Sommets"
    )

    optimal_pt = Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=COULEUR_OPTIMAL,
        markersize=11,
        label="Point optimal"
    )

    handles, _ = ax.get_legend_handles_labels()

    ax.legend(
        handles=[region_patch, sommet_pt, optimal_pt] + handles,
        loc="upper right",
        fontsize=8,
        framealpha=0.9
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()

    return fig


if __name__ == "__main__":
    tracer_surface_realisable()