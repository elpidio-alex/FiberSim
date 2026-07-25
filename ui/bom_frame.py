# -*- coding: utf-8 -*-
"""
ui/bom_frame.py
Ecran de generation du BOM, verification des stocks et export du devis.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from config import Theme


class BOMFrame(tk.Frame):
    def __init__(self, master, bom_calculator, export_manager, db,
                 app_state, inventory_frame):
        super().__init__(master)
        self.bom_calculator = bom_calculator
        self.export_manager = export_manager
        self.db = db
        self.app_state = app_state
        self.inventory_frame = inventory_frame
        self.dernier_resultat = None
        self.mode_theme = "clair"

        self._construire_interface()

    def _construire_interface(self):
        self.label_titre = tk.Label(self, text="BOM & Devis", font=Theme.FONT_TITLE)
        self.label_titre.pack(anchor="w", padx=30, pady=(24, 4))

        self.label_contexte = tk.Label(
            self, text="Aucun projet chargé. Renseignez d'abord les paramètres.",
            font=Theme.FONT_SMALL
        )
        self.label_contexte.pack(anchor="w", padx=30, pady=(0, 16))

        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Button(
            self.toolbar, text="⚙️ Générer le BOM", font=Theme.FONT_NORMAL,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            command=self._generer_bom
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            self.toolbar, text="📄 Exporter CSV", font=Theme.FONT_NORMAL,
            bg=Theme.INFO, fg="white", relief="flat", cursor="hand2",
            command=self._exporter_csv
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            self.toolbar, text="📕 Exporter PDF", font=Theme.FONT_NORMAL,
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            command=self._exporter_pdf
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            self.toolbar, text="💾 Enregistrer dans l'historique", font=Theme.FONT_NORMAL,
            bg=Theme.SUCCESS, fg="white", relief="flat", cursor="hand2",
            command=self._enregistrer_historique
        ).pack(side="left")

        colonnes = ("id", "nom", "type", "qte", "pu", "total", "stock", "statut")
        self.tree = ttk.Treeview(self, columns=colonnes, show="headings", height=14)
        entetes = {
            "id": ("ID", 60),
            "nom": ("Équipement", 220),
            "type": ("Type", 130),
            "qte": ("Qté", 60),
            "pu": ("P.U. (€)", 90),
            "total": ("Total (€)", 100),
            "stock": ("Stock Dispo.", 90),
            "statut": ("Statut", 90),
        }
        for col, (texte, largeur) in entetes.items():
            self.tree.heading(col, text=texte)
            self.tree.column(col, width=largeur, anchor="w")

        self.tree.tag_configure("rupture", foreground=Theme.DANGER)
        self.tree.tag_configure("ok", foreground=Theme.SUCCESS)

        self.tree.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.totaux_frame = tk.Frame(self)
        self.totaux_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.label_totaux = tk.Label(
            self.totaux_frame, text="", font=Theme.FONT_SUBTITLE,
            fg=Theme.PRIMARY_DARK, justify="right"
        )
        self.label_totaux.pack(side="right")

    def on_afficher(self):
        if "nom_projet" in self.app_state:
            c = Theme.get(self.mode_theme)
            self.label_contexte.config(
                text=f"Projet : {self.app_state['nom_projet']} — "
                     f"Surface : {self.app_state['surface_km2']} km² — "
                     f"Densité : {self.app_state['densite_habitants']} hab/km²",
                fg=c["text"]
            )

    def _generer_bom(self):
        if "surface_km2" not in self.app_state:
            messagebox.showwarning(
                "Paramètres manquants",
                "Veuillez d'abord renseigner les paramètres du projet."
            )
            return

        selection = self.inventory_frame.obtenir_selection()

        resultat = self.bom_calculator.generer_bom(
            surface_km2=self.app_state["surface_km2"],
            densite_habitants=self.app_state["densite_habitants"],
            nb_cellules_demande=self.app_state["nb_cellules_demande"],
            equipements_selectionnes=selection,
        )
        self.dernier_resultat = resultat

        self.tree.delete(*self.tree.get_children())
        for ligne in resultat["lignes"]:
            tag = "ok" if ligne["stock_suffisant"] else "rupture"
            statut = "OK" if ligne["stock_suffisant"] else "RUPTURE"
            self.tree.insert("", "end", values=(
                ligne["equipement_id"], ligne["nom_equipement"], ligne["type"],
                ligne["quantite"], f"{ligne['prix_unitaire']:.2f}",
                f"{ligne['prix_total']:.2f}", ligne["stock_disponible"], statut
            ), tags=(tag,))

        self.label_totaux.config(
            text=(
                f"Population totale : {resultat['population_totale']} hab.   "
                f"Cellules : {resultat['nb_cellules_estime']}\n"
                f"Total HT : {resultat['cout_total_ht']:.2f} €   "
                f"TVA (18%) : {resultat['cout_tva']:.2f} €   "
                f"Total TTC : {resultat['cout_total_ttc']:.2f} €"
            )
        )

        ruptures = [l for l in resultat["lignes"] if not l["stock_suffisant"]]
        if ruptures:
            messagebox.showwarning(
                "Alerte Stock",
                f"{len(ruptures)} équipement(s) en rupture de stock ou "
                f"quantité insuffisante. Vérifiez le tableau (lignes en rouge)."
            )

    def _verifier_bom_genere(self):
        if self.dernier_resultat is None:
            messagebox.showwarning("Aucun BOM", "Veuillez d'abord générer le BOM.")
            return False
        return True

    def _exporter_csv(self):
        if not self._verifier_bom_genere():
            return
        succes, resultat = self.export_manager.exporter_csv(
            self.app_state["nom_projet"], self.dernier_resultat
        )
        if succes:
            messagebox.showinfo("Export réussi", f"Fichier CSV généré :\n{resultat}")
        else:
            messagebox.showerror("Erreur", resultat)

    def _exporter_pdf(self):
        if not self._verifier_bom_genere():
            return
        params = {
            "surface_km2": self.app_state["surface_km2"],
            "densite_habitants": self.app_state["densite_habitants"],
        }
        succes, resultat = self.export_manager.exporter_pdf(
            self.app_state["nom_projet"], self.dernier_resultat, params
        )
        if succes:
            messagebox.showinfo("Export réussi", f"Fichier PDF généré :\n{resultat}")
        else:
            messagebox.showerror("Erreur", resultat)

    def _enregistrer_historique(self):
        if not self._verifier_bom_genere():
            return
        if not self.db.is_connected():
            messagebox.showerror("MySQL", "Non connecté à la base de données.")
            return

        lignes_bom = [
            {
                "equipement_id": l["equipement_id"],
                "nom_equipement": l["nom_equipement"],
                "quantite": l["quantite"],
                "prix_unitaire": l["prix_unitaire"],
                "prix_total": l["prix_total"],
                "stock_suffisant": l["stock_suffisant"],
            }
            for l in self.dernier_resultat["lignes"]
        ]

        succes, resultat = self.db.enregistrer_projet(
            nom_projet=self.app_state["nom_projet"],
            surface_km2=self.app_state["surface_km2"],
            densite_habitants=self.app_state["densite_habitants"],
            nb_cellules_estime=self.dernier_resultat["nb_cellules_estime"],
            cout_total_ht=self.dernier_resultat["cout_total_ht"],
            cout_total_ttc=self.dernier_resultat["cout_total_ttc"],
            lignes_bom=lignes_bom,
            utilisateur_id=self.app_state.get("utilisateur_id"),
        )
        if succes:
            messagebox.showinfo("Historique", "Projet enregistré avec succès.")
        else:
            messagebox.showerror("Erreur", str(resultat))

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        c = Theme.get(mode_theme)

        self.config(bg=c["bg"])
        self.label_titre.config(bg=c["bg"], fg=Theme.PRIMARY)
        self.label_contexte.config(bg=c["bg"], fg=c["subtext"])
        self.toolbar.config(bg=c["bg"])
        self.totaux_frame.config(bg=c["bg"])
        self.label_totaux.config(bg=c["bg"])