# -*- coding: utf-8 -*-
"""
ui/history_frame.py
Ecran d'historique des projets et devis enregistres en MySQL.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from config import Theme


class HistoryFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.mode_theme = "clair"

        self._construire_interface()

    def _construire_interface(self):
        self.label_titre = tk.Label(
            self, text="Historique des Projets", font=Theme.FONT_TITLE
        )
        self.label_titre.pack(anchor="w", padx=30, pady=(24, 4))

        self.label_sous_titre = tk.Label(
            self, text="Liste des devis générés et enregistrés en base MySQL",
            font=Theme.FONT_SMALL
        )
        self.label_sous_titre.pack(anchor="w", padx=30, pady=(0, 16))

        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Button(
            self.toolbar, text="🔄 Actualiser", font=Theme.FONT_SMALL,
            bg=Theme.INFO, fg="white", relief="flat", cursor="hand2",
            command=self.on_afficher
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            self.toolbar, text="🗑️ Supprimer le projet sélectionné", font=Theme.FONT_SMALL,
            bg=Theme.DANGER, fg="white", relief="flat", cursor="hand2",
            command=self._supprimer_selection
        ).pack(side="left")

        colonnes = ("id", "nom", "surface", "densite", "cellules", "ht", "ttc", "date")
        self.tree = ttk.Treeview(self, columns=colonnes, show="headings", height=16)
        entetes = {
            "id": ("ID", 40),
            "nom": ("Projet", 200),
            "surface": ("Surface (km²)", 90),
            "densite": ("Densité", 90),
            "cellules": ("Cellules", 70),
            "ht": ("Total HT (€)", 100),
            "ttc": ("Total TTC (€)", 100),
            "date": ("Date", 140),
        }
        for col, (texte, largeur) in entetes.items():
            self.tree.heading(col, text=texte)
            self.tree.column(col, width=largeur, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def on_afficher(self):
        if not self.db.is_connected():
            messagebox.showerror("MySQL", "Non connecté à la base de données.")
            return

        self.tree.delete(*self.tree.get_children())
        projets = self.db.lister_projets()
        for p in projets:
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nom_projet"], p["surface_km2"],
                p["densite_habitants"], p["nb_cellules_estime"],
                f"{p['cout_total_ht']:.2f}", f"{p['cout_total_ttc']:.2f}",
                p["date_creation"].strftime("%d/%m/%Y %H:%M")
                if p["date_creation"] else ""
            ))

    def _supprimer_selection(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un projet à supprimer.")
            return

        if not messagebox.askyesno("Confirmation",
                                    "Supprimer définitivement ce projet et son devis ?"):
            return

        projet_id = int(selection[0])
        if self.db.supprimer_projet(projet_id):
            self.on_afficher()
        else:
            messagebox.showerror("Erreur", "La suppression a échoué.")

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        c = Theme.get(mode_theme)

        self.config(bg=c["bg"])
        self.label_titre.config(bg=c["bg"], fg=Theme.PRIMARY)
        self.label_sous_titre.config(bg=c["bg"], fg=c["subtext"])
        self.toolbar.config(bg=c["bg"])