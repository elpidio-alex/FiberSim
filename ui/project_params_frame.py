# -*- coding: utf-8 -*-
"""
ui/project_params_frame.py
Ecran de saisie des parametres du projet urbain
(surface, densite d'habitants, nombre de cellules souhaite).
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme


class ProjectParamsFrame(tk.Frame):
    def __init__(self, master, app_state, on_params_valides):
        super().__init__(master)
        self.app_state = app_state
        self.on_params_valides = on_params_valides
        self.mode_theme = "clair"

        self.labels_champs = []
        self.entries_champs = []

        self._construire_interface()

    def _construire_interface(self):
        self.label_titre = tk.Label(
            self, text="Paramètres du Projet Urbain", font=Theme.FONT_TITLE
        )
        self.label_titre.pack(anchor="w", padx=30, pady=(24, 4))

        self.label_sous_titre = tk.Label(
            self, text="Renseignez les caractéristiques de la zone urbaine à couvrir",
            font=Theme.FONT_SMALL
        )
        self.label_sous_titre.pack(anchor="w", padx=30, pady=(0, 20))

        self.carte = tk.Frame(self, padx=30, pady=30, highlightthickness=1)
        self.carte.pack(padx=30, fill="x")

        self._creer_champ(self.carte, "Nom du projet", "nom_projet_var", 0,
                           valeur_defaut="Quartier Test - Lomé")
        self._creer_champ(self.carte, "Surface à couvrir (km²)", "surface_var", 1,
                           valeur_defaut="2")
        self._creer_champ(self.carte, "Densité de population (habitants/km²)",
                           "densite_var", 2, valeur_defaut="7500")
        self._creer_champ(self.carte, "Nombre de cellules souhaité (minimum)",
                           "cellules_var", 3, valeur_defaut="1")

        self.label_info = tk.Label(
            self.carte, text="ℹ️ Le nombre de cellules réellement utilisé sera le "
                       "maximum entre votre saisie et l'estimation calculée "
                       "à partir de la population totale.",
            font=Theme.FONT_SMALL, fg=Theme.INFO,
            wraplength=500, justify="left"
        )
        self.label_info.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.bouton_valider = tk.Button(
            self.carte, text="✅ Valider et Générer le BOM", font=Theme.FONT_SUBTITLE,
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            activebackground=Theme.ACCENT_DARK, activeforeground="white",
            command=self._valider
        )
        self.bouton_valider.grid(row=5, column=0, columnspan=2, sticky="ew",
                                  pady=(24, 0), ipady=8)

        self.carte.grid_columnconfigure(1, weight=1)

    def _creer_champ(self, parent, label, nom_var, ligne, valeur_defaut=""):
        lbl = tk.Label(parent, text=label, font=Theme.FONT_NORMAL, anchor="w")
        lbl.grid(row=ligne, column=0, sticky="w", pady=8, padx=(0, 20))
        self.labels_champs.append(lbl)

        var = tk.StringVar(value=valeur_defaut)
        entry = tk.Entry(parent, textvariable=var, font=Theme.FONT_NORMAL,
                          relief="solid", bd=1, width=25)
        entry.grid(row=ligne, column=1, sticky="ew", pady=8, ipady=4)
        self.entries_champs.append(entry)

        setattr(self, nom_var, var)

    def _valider(self):
        try:
            nom_projet = self.nom_projet_var.get().strip()
            surface = float(self.surface_var.get())
            densite = float(self.densite_var.get())
            nb_cellules = int(self.cellules_var.get())

            if not nom_projet:
                raise ValueError("Le nom du projet ne peut pas être vide.")
            if surface <= 0 or densite <= 0 or nb_cellules < 0:
                raise ValueError("Les valeurs doivent être positives.")

        except ValueError as e:
            messagebox.showerror("Paramètres invalides",
                                  f"Veuillez vérifier vos saisies.\n{e}")
            return

        self.app_state["nom_projet"] = nom_projet
        self.app_state["surface_km2"] = surface
        self.app_state["densite_habitants"] = densite
        self.app_state["nb_cellules_demande"] = nb_cellules

        self.on_params_valides()

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        c = Theme.get(mode_theme)

        self.config(bg=c["bg"])
        self.label_titre.config(bg=c["bg"], fg=Theme.PRIMARY)
        self.label_sous_titre.config(bg=c["bg"], fg=c["subtext"])
        self.carte.config(bg=c["card"], highlightbackground=c["border"])
        self.label_info.config(bg=c["card"])

        for lbl in self.labels_champs:
            lbl.config(bg=c["card"], fg=c["text"])
