"""
Date : 01/08/2026
Auteur : Elpidio Alexis AMOUSSOU
Email : amoussouelpidioalexis@gmail.com

"""
# -*- coding: utf-8 -*-
"""
ui/inventory_frame.py
Ecran d'inventaire : import obligatoire d'un fichier Excel par l'utilisateur,
puis CRUD complet (ajouter, modifier, supprimer) sur les equipements.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from config import Theme


class EquipmentFormDialog(tk.Toplevel):
    """Fenetre modale pour ajouter ou modifier un equipement."""

    def __init__(self, master, mode_theme, titre, valeurs_initiales=None,
                 on_valider=None):
        super().__init__(master)
        self.title(titre)
        self.resizable(False, False)
        self.on_valider = on_valider
        self.valeurs_initiales = valeurs_initiales or {}

        c = Theme.get(mode_theme)
        self.configure(bg=c["card"])

        self.champs = {}
        self._construire_formulaire(c)

        self.transient(master)
        self.grab_set()

    def _construire_formulaire(self, c):
        specs = [
            ("ID", "ID"),
            ("Nom Équipement", "Nom Équipement"),
            ("Type", "Type"),
            ("Fabricant", "Fabricant"),
            ("Prix Unitaire (€)", "Prix Unitaire (€)"),
            ("Disponibilité (stock)", "Disponibilité (stock)"),
            ("Spécifications Techniques", "Spécifications Techniques"),
        ]

        conteneur = tk.Frame(self, bg=c["card"], padx=24, pady=20)
        conteneur.pack(fill="both", expand=True)

        LARGEUR_ENTRY = 32

        for i, (cle, label) in enumerate(specs):
            tk.Label(
                conteneur, text=label, font=Theme.FONT_NORMAL,
                bg=c["card"], fg=c["text"], anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=6, padx=(0, 16))

            valeur_defaut = self.valeurs_initiales.get(cle, "")
            entry = tk.Entry(
                conteneur, font=("Consolas", 10), width=LARGEUR_ENTRY,
                relief="solid", bd=1
            )
            entry.insert(0, str(valeur_defaut))
            entry.grid(row=i, column=1, sticky="ew", pady=6, ipady=4)
            self.champs[cle] = entry

        # L'ID n'est pas modifiable en mode edition (cle primaire du fichier)
        if "ID" in self.valeurs_initiales:
            self.champs["ID"].config(state="disabled")

        bouton = tk.Button(
            conteneur, text="✅ Valider", font=Theme.FONT_SUBTITLE,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            command=self._valider
        )
        bouton.grid(row=len(specs), column=0, columnspan=2, sticky="ew",
                    pady=(16, 0), ipady=8)

        conteneur.grid_columnconfigure(1, weight=1)

    def _valider(self):
        try:
            donnees = {
                "ID": self.champs["ID"].get().strip(),
                "Nom Équipement": self.champs["Nom Équipement"].get().strip(),
                "Type": self.champs["Type"].get().strip(),
                "Fabricant": self.champs["Fabricant"].get().strip(),
                "Prix Unitaire (€)": float(self.champs["Prix Unitaire (€)"].get()),
                "Disponibilité (stock)": int(self.champs["Disponibilité (stock)"].get()),
                "Spécifications Techniques": self.champs["Spécifications Techniques"].get().strip(),
            }

            if not donnees["ID"] or not donnees["Nom Équipement"]:
                raise ValueError("L'ID et le nom de l'équipement sont obligatoires.")

        except ValueError as e:
            messagebox.showerror("Champs invalides", f"Veuillez vérifier vos saisies.\n{e}")
            return

        if self.on_valider:
            self.on_valider(donnees)
        self.destroy()


class InventoryFrame(tk.Frame):
    def __init__(self, master, equipment_manager, app_state):
        super().__init__(master)
        self.equipment_manager = equipment_manager
        self.app_state = app_state
        self.mode_theme = "clair"

        self._construire_interface()
        self._rafraichir_etat_vide()

    def _construire_interface(self):
        self.label_titre = tk.Label(
            self, text="Inventaire et Gestion des Équipements",
            font=Theme.FONT_TITLE
        )
        self.label_titre.pack(anchor="w", padx=30, pady=(24, 4))

        self.label_sous_titre = tk.Label(
            self, text="Importez un fichier Excel pour commencer",
            font=Theme.FONT_SMALL
        )
        self.label_sous_titre.pack(anchor="w", padx=30, pady=(0, 16))

        # Barre d'outils
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill="x", padx=30, pady=(0, 10))

        self.bouton_importer = tk.Button(
            self.toolbar, text="📂 Importer un fichier Excel", font=Theme.FONT_SMALL,
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            command=self._importer_fichier
        )
        self.bouton_importer.pack(side="left", padx=(0, 8))

        self.bouton_ajouter = tk.Button(
            self.toolbar, text="➕ Ajouter", font=Theme.FONT_SMALL,
            bg=Theme.SUCCESS, fg="white", relief="flat", cursor="hand2",
            command=self._ajouter_equipement, state="disabled"
        )
        self.bouton_ajouter.pack(side="left", padx=(0, 8))

        self.bouton_modifier = tk.Button(
            self.toolbar, text="✏️ Modifier", font=Theme.FONT_SMALL,
            bg=Theme.INFO, fg="white", relief="flat", cursor="hand2",
            command=self._modifier_equipement, state="disabled"
        )
        self.bouton_modifier.pack(side="left", padx=(0, 8))

        self.bouton_supprimer = tk.Button(
            self.toolbar, text="🗑️ Supprimer", font=Theme.FONT_SMALL,
            bg=Theme.DANGER, fg="white", relief="flat", cursor="hand2",
            command=self._supprimer_equipement, state="disabled"
        )
        self.bouton_supprimer.pack(side="left", padx=(0, 8))

        self.bouton_sauvegarder = tk.Button(
            self.toolbar, text="💾 Sauvegarder le fichier", font=Theme.FONT_SMALL,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            command=self._sauvegarder_fichier, state="disabled"
        )
        self.bouton_sauvegarder.pack(side="left", padx=(0, 8))

        self.bouton_tout_selectionner = tk.Button(
            self.toolbar, text="✅ Tout sélectionner", font=Theme.FONT_SMALL,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            command=self._tout_selectionner, state="disabled"
        )
        self.bouton_tout_selectionner.pack(side="left", padx=(0, 8))

        self.label_statut = tk.Label(self.toolbar, text="", font=Theme.FONT_SMALL)
        self.label_statut.pack(side="right")

        self.label_source = tk.Label(self, text="", font=Theme.FONT_SMALL)
        self.label_source.pack(anchor="w", padx=30, pady=(0, 6))

        # Zone d'etat vide (avant import)
        self.frame_etat_vide = tk.Frame(self)
        self.label_etat_vide = tk.Label(
            self.frame_etat_vide,
            text="📂\n\nAucun fichier chargé.\n"
                 "Cliquez sur \"Importer un fichier Excel\" pour commencer.",
            font=Theme.FONT_NORMAL, justify="center"
        )
        self.label_etat_vide.pack(expand=True)

        # Tableau des equipements
        colonnes = ("id", "nom", "type", "fabricant", "prix", "stock", "specs")
        self.tree = ttk.Treeview(self, columns=colonnes, show="headings",
                                  selectmode="extended", height=18)

        entetes = {
            "id": ("ID", 60),
            "nom": ("Équipement", 200),
            "type": ("Type", 120),
            "fabricant": ("Fabricant", 100),
            "prix": ("Prix Unit. (€)", 100),
            "stock": ("Stock", 70),
            "specs": ("Spécifications", 300),
        }
        for col, (texte, largeur) in entetes.items():
            self.tree.heading(col, text=texte)
            self.tree.column(col, width=largeur, anchor="w")

        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

    def _rafraichir_etat_vide(self):
        """Affiche soit l'ecran d'etat vide, soit le tableau, selon l'import."""
        if self.equipment_manager.est_charge():
            self.frame_etat_vide.pack_forget()
            self.tree.pack(side="left", fill="both", expand=True,
                            padx=(30, 0), pady=(0, 20))
            self.scrollbar_y.pack(side="left", fill="y", pady=(0, 20), padx=(0, 30))
            for btn in (self.bouton_ajouter, self.bouton_modifier,
                        self.bouton_supprimer, self.bouton_sauvegarder,
                        self.bouton_tout_selectionner):
                btn.config(state="normal")
        else:
            self.tree.pack_forget()
            self.scrollbar_y.pack_forget()
            self.frame_etat_vide.pack(fill="both", expand=True, padx=30, pady=(0, 20))
            for btn in (self.bouton_ajouter, self.bouton_modifier,
                        self.bouton_supprimer, self.bouton_sauvegarder,
                        self.bouton_tout_selectionner):
                btn.config(state="disabled")

    # --------------------------------------------------------
    def _importer_fichier(self):
        chemin = filedialog.askopenfilename(
            title="Importer un fichier Excel d'équipements",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")]
        )
        if not chemin:
            return

        succes, message = self.equipment_manager.charger(chemin)
        self._traiter_resultat(succes, message)
        if succes:
            nom_fichier = chemin.replace("\\", "/").split("/")[-1]
            self.label_source.config(text=f"Source actuelle : {nom_fichier}", fg=Theme.INFO)
            self.label_sous_titre.config(
                text="Sélectionnez un équipement pour le modifier ou le supprimer"
            )

    def _traiter_resultat(self, succes, message):
        if not succes:
            messagebox.showerror("Erreur", message)
            self.label_statut.config(text="❌ Échec", fg=Theme.DANGER)
            return

        self._rafraichir_tableau()
        self._rafraichir_etat_vide()
        self.label_statut.config(text=f"✅ {message}", fg=Theme.SUCCESS)

    def _rafraichir_tableau(self):
        self.tree.delete(*self.tree.get_children())
        for eq in self.equipment_manager.obtenir_tous():
            self.tree.insert("", "end", iid=eq["ID"], values=(
                eq["ID"], eq["Nom Équipement"], eq["Type"], eq["Fabricant"],
                f"{eq['Prix Unitaire (€)']:.2f}", eq["Disponibilité (stock)"],
                eq["Spécifications Techniques"],
            ))

    def _tout_selectionner(self):
        self.tree.selection_set(self.tree.get_children())

    def obtenir_selection(self):
        selection = self.tree.selection()
        return list(selection) if selection else None

    # --------------------------------------------------------
    # CRUD
    # --------------------------------------------------------
    def _ajouter_equipement(self):
        def on_valider(donnees):
            succes, message = self.equipment_manager.ajouter_equipement(donnees)
            if succes:
                self._rafraichir_tableau()
                self.label_statut.config(text=f"✅ {message}", fg=Theme.SUCCESS)
            else:
                messagebox.showerror("Erreur", message)

        EquipmentFormDialog(
            self, self.mode_theme, "Ajouter un équipement", on_valider=on_valider
        )

    def _modifier_equipement(self):
        selection = self.tree.selection()
        if len(selection) != 1:
            messagebox.showwarning(
                "Sélection requise",
                "Sélectionnez un seul équipement à modifier."
            )
            return

        equipement_id = selection[0]
        valeurs = self.equipment_manager.obtenir_par_id(equipement_id)
        if valeurs is None:
            return

        def on_valider(donnees):
            succes, message = self.equipment_manager.modifier_equipement(
                equipement_id, donnees
            )
            if succes:
                self._rafraichir_tableau()
                self.label_statut.config(text=f"✅ {message}", fg=Theme.SUCCESS)
            else:
                messagebox.showerror("Erreur", message)

        EquipmentFormDialog(
            self, self.mode_theme, "Modifier l'équipement",
            valeurs_initiales=valeurs, on_valider=on_valider
        )

    def _supprimer_equipement(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez au moins un équipement.")
            return

        if not messagebox.askyesno(
            "Confirmation",
            f"Supprimer définitivement {len(selection)} équipement(s) ?"
        ):
            return

        for equipement_id in selection:
            self.equipment_manager.supprimer_equipement(equipement_id)

        self._rafraichir_tableau()
        self.label_statut.config(text="✅ Suppression effectuée", fg=Theme.SUCCESS)

    def _sauvegarder_fichier(self):
        succes, message = self.equipment_manager.sauvegarder()
        if succes:
            messagebox.showinfo("Sauvegarde", message)
        else:
            messagebox.showerror("Erreur", message)

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        c = Theme.get(mode_theme)

        self.config(bg=c["bg"])
        self.label_titre.config(bg=c["bg"], fg=Theme.PRIMARY)
        self.label_sous_titre.config(bg=c["bg"], fg=c["subtext"])
        self.toolbar.config(bg=c["bg"])
        self.label_statut.config(bg=c["bg"])
        self.label_source.config(bg=c["bg"], fg=c["subtext"])
        self.frame_etat_vide.config(bg=c["bg"])
        self.label_etat_vide.config(bg=c["bg"], fg=c["subtext"])