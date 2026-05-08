import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calculs import (
    trouver_solution_optimale_graphique,
    resoudre_simplexe,
    verifier_utilisation_ressources,
    NOMS_4VAR,
)
from graphique import tracer_surface_realisable
from simplexe import exporter_resultats

ROSE_CLAIR = "#FFB6C1"

PF = ("Arial", 15, "bold")
PS = ("Arial", 10, "bold")
PM = ("Courier New", 10)


class ApplicationPL(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Optimisation des Stocks de Medicaments")
        self.geometry("1200x820")
        self.minsize(900, 650)
        self.configure(bg="white")
        self._styles()
        self._entete()
        self._notebook()
        self._statut()

    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background="white", borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=ROSE_CLAIR,
                    foreground="black",
                    font=("Arial", 10, "bold"),
                    padding=[14, 6])
        s.map("TNotebook.Tab",
              background=[("selected", ROSE_CLAIR)],
              foreground=[("selected", "black")])
        s.configure("Treeview",
                    background="white", fieldbackground="white",
                    foreground="black", rowheight=26, font=("Arial", 10))
        s.configure("Treeview.Heading",
                    background=ROSE_CLAIR, foreground="black",
                    font=("Arial", 10, "bold"))
        s.map("Treeview",
              background=[("selected", ROSE_CLAIR)],
              foreground=[("selected", "black")])

    def _entete(self):
        f = tk.Frame(self, bg=ROSE_CLAIR, height=55)
        f.pack(fill="x")
        f.pack_propagate(False)
        tk.Label(f, text="Optimisation des Stocks de Medicaments",
                 font=("Arial", 16, "bold"), bg=ROSE_CLAIR, fg="black").pack(pady=(12, 0))

    def _notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=8)
        self.tab1 = OngletGraphique(self.nb, self)
        self.nb.add(self.tab1, text="  Methode Graphique (2 variables)  ")
        self.tab2 = OngletSimplexe(self.nb, self)
        self.nb.add(self.tab2, text="  Methode du Simplexe (4 variables)  ")

    def _statut(self):
        self.msg = tk.StringVar(value="Pret.")
        tk.Label(self, textvariable=self.msg,
                 bg=ROSE_CLAIR, fg="black",
                 font=("Arial", 9), anchor="w", padx=10
                 ).pack(fill="x", side="bottom")

    def set_statut(self, txt):
        self.msg.set(txt)


class OngletGraphique(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        self._build()

    def _build(self):
        left = tk.Frame(self, bg="white", width=360)
        left.pack(side="left", fill="y", padx=8, pady=8)
        left.pack_propagate(False)
        right = tk.Frame(self, bg="white")
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self._formulation(left)
        self._boutons(left)
        self._tableau(left)
        self._solution(left)
        self._zone_graphique(right)

    def _formulation(self, p):
        f = tk.LabelFrame(p, text="  Formulation  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x", pady=(0, 8))
        lignes = [
            ("Objectif :", "Max Z = 2x1 + 3x2"),
            ("", ""),
            ("Contraintes :", "5x1 + 8x2 <= 500"),
            ("", "x1 + x2   <= 100"),
            ("", "x1        <= 80"),
            ("", "x2        <= 60"),
            ("", "x1, x2    >= 0"),
        ]
        for lbl, val in lignes:
            row = tk.Frame(f, bg=ROSE_CLAIR)
            row.pack(fill="x", padx=8, pady=1)
            if lbl:
                tk.Label(row, text=lbl, bg=ROSE_CLAIR, fg="black",
                         font=("Arial", 9, "bold"),
                         width=14, anchor="w").pack(side="left")
            if val:
                tk.Label(row, text=val, bg=ROSE_CLAIR,
                         fg="black", font=PM, anchor="w").pack(side="left")

    def _btn(self, parent, texte, cmd, bg=ROSE_CLAIR):
        b = tk.Button(parent, text=texte, command=cmd,
                      bg=bg, fg="black", font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2",
                      activebackground=ROSE_CLAIR,
                      activeforeground="black", pady=7)
        b.bind("<Enter>", lambda e: b.configure(bg=ROSE_CLAIR))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        return b

    def _boutons(self, p):
        f = tk.Frame(p, bg="white")
        f.pack(fill="x", pady=(0, 8))
        self._btn(f, "Calculer", self._calculer).pack(fill="x", pady=2)
        self._btn(f, "Afficher le graphique", self._graphique).pack(fill="x", pady=2)
        self._btn(f, "Exporter", self._exporter).pack(fill="x", pady=2)

    def _tableau(self, p):
        f = tk.LabelFrame(p, text="  Sommets  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x", pady=(0, 8))
        cols = ("pt", "x1", "x2", "z")
        self.tree = ttk.Treeview(f, columns=cols,
                                 show="headings", height=6)
        for col, titre, w in [("pt", "Pt", 45), ("x1", "x1", 70),
                              ("x2", "x2", 70), ("z", "Z", 110)]:
            self.tree.heading(col, text=titre)
            self.tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        sb.pack(side="right", fill="y", pady=4)

    def _solution(self, p):
        f = tk.LabelFrame(p, text="  Solution optimale  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x")
        self.v_x1 = self._kv(f, "x1 (Paracetamol) :", "---")
        self.v_x2 = self._kv(f, "x2 (Doliprane) :", "---")
        self.v_z = self._kv(f, "Profit max Z :", "---")

    def _kv(self, p, k, v):
        row = tk.Frame(p, bg=ROSE_CLAIR)
        row.pack(fill="x", padx=8, pady=3)
        tk.Label(row, text=k, bg=ROSE_CLAIR, fg="black",
                 font=("Arial", 9, "bold"),
                 width=22, anchor="w").pack(side="left")
        var = tk.StringVar(value=v)
        tk.Label(row, textvariable=var, bg=ROSE_CLAIR,
                 fg="black", font=("Courier New", 11, "bold")).pack(side="left")
        return var

    def _zone_graphique(self, p):
        tk.Label(p, text="Graphique",
                 bg="white", fg="black",
                 font=("Arial", 9)).pack(anchor="w", padx=4)
        self.frame_g = tk.Frame(p, bg="white")
        self.frame_g.pack(fill="both", expand=True)
        tk.Label(self.frame_g,
                 text="Cliquez sur 'Afficher le graphique'",
                 bg="white", fg="black",
                 font=("Arial", 11)).pack(expand=True)

    def _calculer(self):
        try:
            sol = trouver_solution_optimale_graphique()
            for item in self.tree.get_children():
                self.tree.delete(item)
            pts = ["D", "E", "A", "B", "C"]
            for i, (x, y, z) in enumerate(sol["sommets"]):
                opt = abs(x - sol["optimal_x"]) < 1e-4 and \
                      abs(y - sol["optimal_y"]) < 1e-4
                nom = pts[i] if i < len(pts) else f"S{i}"
                tag = "opt" if opt else ""
                self.tree.insert("", "end",
                                 values=(nom, x, y, z), tags=(tag,))
            self.tree.tag_configure("opt",
                                    background=ROSE_CLAIR,
                                    foreground="black")
            self.v_x1.set(str(sol["optimal_x"]))
            self.v_x2.set(str(sol["optimal_y"]))
            self.v_z.set(str(sol["profit_max"]))
            self.app.set_statut(
                f"x1={sol['optimal_x']}  x2={sol['optimal_y']}  Z={sol['profit_max']}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _graphique(self):
        try:
            for w in self.frame_g.winfo_children():
                w.destroy()
            fig = tracer_surface_realisable()
            canvas = FigureCanvasTkAgg(fig, master=self.frame_g)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.app.set_statut("Graphique affiche.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _exporter(self):
        try:
            chemin = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Texte", "*.txt")],
                initialfile="resultats_graphique.txt")
            if not chemin:
                return
            sol = trouver_solution_optimale_graphique()
            lignes = ["=" * 60, "  RESULTATS - METHODE GRAPHIQUE", "=" * 60,
                      "", "  Max Z = 2x1 + 3x2", "", "  Sommets :"]
            for x, y, z in sol["sommets"]:
                opt = " <- OPTIMAL" if (abs(x - sol["optimal_x"]) < 1e-4 and
                                        abs(y - sol["optimal_y"]) < 1e-4) else ""
                lignes.append(f"    ({x}, {y}) -> Z={z}{opt}")
            lignes += ["",
                       f"  x1 = {sol['optimal_x']}",
                       f"  x2 = {sol['optimal_y']}",
                       f"  Z  = {sol['profit_max']}",
                       "", "=" * 60]
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("\n".join(lignes))
            messagebox.showinfo("OK", f"Sauvegarde :\n{chemin}")
            self.app.set_statut(f"Exporte -> {chemin}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class OngletSimplexe(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        self._sol = None
        self._build()

    def _build(self):
        left = tk.Frame(self, bg="white", width=380)
        left.pack(side="left", fill="y", padx=8, pady=8)
        left.pack_propagate(False)
        right = tk.Frame(self, bg="white")
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self._formulation(left)
        self._boutons(left)
        self._variables(left)
        self._tableau_res(right)
        self._zone_sat(right)

    def _formulation(self, p):
        f = tk.LabelFrame(p, text="  Formulation (4 medicaments)  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x", pady=(0, 8))
        for txt in [
            "Max Z = 2x1 + 3x2 + 4x3 + 5x4", "",
            "5x1+8x2+6x3+10x4 <= 800",
            "x1+x2+x3+x4      <= 150",
            "x1<=80  x2<=60  x3<=50  x4<=40",
            "x1, x2, x3, x4 >= 0",
        ]:
            tk.Label(f, text=txt, bg=ROSE_CLAIR,
                     fg="black", font=PM,
                     anchor="w").pack(fill="x", padx=10, pady=1)

    def _btn(self, parent, texte, cmd, bg=ROSE_CLAIR):
        b = tk.Button(parent, text=texte, command=cmd,
                      bg=bg, fg="black", font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2",
                      activebackground=ROSE_CLAIR,
                      activeforeground="black", pady=7)
        b.bind("<Enter>", lambda e: b.configure(bg=ROSE_CLAIR))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        return b

    def _boutons(self, p):
        f = tk.Frame(p, bg="white")
        f.pack(fill="x", pady=(0, 8))
        self._btn(f, "Resoudre", self._resoudre).pack(fill="x", pady=2)
        self._btn(f, "Exporter", self._exporter).pack(fill="x", pady=2)

    def _variables(self, p):
        f = tk.LabelFrame(p, text="  Variables optimales  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x")
        self.vars_lbl = {}
        for nom in NOMS_4VAR:
            row = tk.Frame(f, bg=ROSE_CLAIR)
            row.pack(fill="x", padx=8, pady=3)
            tk.Label(row, text=f"{nom} :", bg=ROSE_CLAIR,
                     fg="black", font=("Arial", 9, "bold"),
                     width=15, anchor="w").pack(side="left")
            var = tk.StringVar(value="---")
            tk.Label(row, textvariable=var, bg=ROSE_CLAIR,
                     fg="black",
                     font=("Courier New", 11, "bold")).pack(side="left")
            self.vars_lbl[nom] = var

        tk.Frame(f, bg=ROSE_CLAIR, height=1).pack(fill="x", padx=8, pady=4)
        row = tk.Frame(f, bg=ROSE_CLAIR)
        row.pack(fill="x", padx=8, pady=3)
        tk.Label(row, text="Profit max Z :", bg=ROSE_CLAIR,
                 fg="black", font=("Arial", 10, "bold"),
                 width=15, anchor="w").pack(side="left")
        self.v_profit = tk.StringVar(value="---")
        tk.Label(row, textvariable=self.v_profit, bg=ROSE_CLAIR,
                 fg="black",
                 font=("Courier New", 13, "bold")).pack(side="left")

    def _tableau_res(self, p):
        tk.Label(p, text="Utilisation des ressources",
                 bg="white", fg="black",
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=4)
        f = tk.Frame(p, bg="white")
        f.pack(fill="both", expand=True, pady=(4, 8))
        cols = ("c", "u", "l", "m", "s")
        self.tree_res = ttk.Treeview(f, columns=cols,
                                     show="headings", height=8)
        for col, titre, w in [("c", "Contrainte", 240), ("u", "Utilise", 80),
                              ("l", "Limite", 70), ("m", "Marge", 70),
                              ("s", "Statut", 90)]:
            self.tree_res.heading(col, text=titre)
            self.tree_res.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(f, orient="vertical",
                           command=self.tree_res.yview)
        self.tree_res.configure(yscrollcommand=sb.set)
        self.tree_res.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_res.tag_configure("sat",
                                    background=ROSE_CLAIR,
                                    foreground="black")
        self.tree_res.tag_configure("ok",
                                    background="white",
                                    foreground="black")

    def _zone_sat(self, p):
        f = tk.LabelFrame(p, text="  Contraintes saturees  ",
                          bg=ROSE_CLAIR, fg="black",
                          font=PS, bd=1, relief="solid")
        f.pack(fill="x")
        self.txt_sat = tk.Text(f, bg=ROSE_CLAIR, fg="black",
                               font=PM, height=4, wrap="word",
                               relief="flat", bd=0)
        self.txt_sat.pack(fill="x", padx=8, pady=6)
        self.txt_sat.insert("end", "Cliquez sur 'Resoudre' pour voir les resultats.")
        self.txt_sat.configure(state="disabled")

    def _resoudre(self):
        try:
            self._sol = resoudre_simplexe()
            if not self._sol["succes"]:
                messagebox.showerror("Erreur", self._sol["message"])
                return

            for nom, val in zip(self._sol["noms"], self._sol["variables"]):
                self.vars_lbl[nom].set(str(val))
            self.v_profit.set(str(self._sol["profit_max"]))

            for item in self.tree_res.get_children():
                self.tree_res.delete(item)
            for r in verifier_utilisation_ressources(self._sol["variables"]):
                tag = "sat" if r["saturee"] else "ok"
                s = "SATUREE" if r["saturee"] else "OK"
                self.tree_res.insert("", "end",
                                     values=(r["nom"], r["utilisation"],
                                             r["limite"], r["marge"], s),
                                     tags=(tag,))

            self.txt_sat.configure(state="normal")
            self.txt_sat.delete("1.0", "end")
            if self._sol["contraintes_saturees"]:
                for s in self._sol["contraintes_saturees"]:
                    self.txt_sat.insert("end", f"  * {s}\n")
            else:
                self.txt_sat.insert("end", "  Aucune contrainte saturee.")
            self.txt_sat.configure(state="disabled")

            self.app.set_statut(
                f"Z={self._sol['profit_max']}  |  " +
                "  ".join(f"{n}={v}" for n, v in
                          zip(self._sol["noms"], self._sol["variables"])))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _exporter(self):
        if self._sol is None:
            messagebox.showwarning("Attention",
                                   "Lancez d'abord 'Resoudre'.")
            return
        chemin = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt")],
            initialfile="resultats_simplexe.txt")
        if chemin:
            exporter_resultats(self._sol, chemin)
            messagebox.showinfo("OK", f"Sauvegarde :\n{chemin}")
            self.app.set_statut(f"Exporte -> {chemin}")


if __name__ == "__main__":
    app = ApplicationPL()
    app.mainloop()