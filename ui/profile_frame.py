# -*- coding: utf-8 -*-
"""
ui/profile_frame.py
Ecran de modification du profil utilisateur
(nom d'utilisateur, email, mot de passe).
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme


class ProfileFrame(tk.Frame):
    def __init__(self, master, db, app_state, on_profil_modifie=None):
        super().__init__(master)
        self.db = db
        self.app_state = app_state
        self.on_profil_modifie = on_profil_modifie
        self.mode_theme = "clair"

        self._construire_interface()

    def _construire_interface(self):
        self.label_titre = tk.Label(
            self, text="Mon Profil", font=Theme.FONT_TITLE
        )
        self.label_titre.pack(anchor="w", padx=30, pady=(24, 4))

        self.label_sous_titre = tk.Label(
            self, text="Modifiez vos informations de compte",
            font=Theme.FONT_SMALL
        )
        self.label_sous_titre.pack(anchor="w", padx=30, pady=(0, 20))

        self.carte = tk.Frame(self, padx=30, pady=30, highlightthickness=1)
        self.carte.pack(padx=30, fill="x")

        LARGEUR_ENTRY = 32

        # Nom d'utilisateur
        self.label_username = tk.Label(self.carte, text="Nom d'utilisateur",
                                        font=Theme.FONT_NORMAL, anchor="w")
        self.label_username.grid(row=0, column=0, sticky="w", pady=8, padx=(0, 20))
        self.entry_username = tk.Entry(self.carte, font=("Consolas", 10),
                                        width=LARGEUR_ENTRY, relief="solid", bd=1)
        self.entry_username.grid(row=0, column=1, sticky="ew", pady=8, ipady=4)

        # Email
        self.label_email = tk.Label(self.carte, text="Adresse email",
                                     font=Theme.FONT_NORMAL, anchor="w")
        self.label_email.grid(row=1, column=0, sticky="w", pady=8, padx=(0, 20))
        self.entry_email = tk.Entry(self.carte, font=("Consolas", 10),
                                     width=LARGEUR_ENTRY, relief="solid", bd=1)
        self.entry_email.grid(row=1, column=1, sticky="ew", pady=8, ipady=4)

        # Separateur
        self.label_separateur = tk.Label(
            self.carte, text="— Laissez vide pour ne pas changer le mot de passe —",
            font=Theme.FONT_SMALL
        )
        self.label_separateur.grid(row=2, column=0, columnspan=2, pady=(14, 6))

        # Nouveau mot de passe
        self.label_password = tk.Label(self.carte, text="Nouveau mot de passe",
                                        font=Theme.FONT_NORMAL, anchor="w")
        self.label_password.grid(row=3, column=0, sticky="w", pady=8, padx=(0, 20))
        self.entry_password = tk.Entry(self.carte, font=("Consolas", 10),
                                        width=LARGEUR_ENTRY, relief="solid", bd=1, show="•")
        self.entry_password.grid(row=3, column=1, sticky="ew", pady=8, ipady=4)

        # Confirmation mot de passe
        self.label_password_confirm = tk.Label(self.carte, text="Confirmer le mot de passe",
                                                 font=Theme.FONT_NORMAL, anchor="w")
        self.label_password_confirm.grid(row=4, column=0, sticky="w", pady=8, padx=(0, 20))
        self.entry_password_confirm = tk.Entry(self.carte, font=("Consolas", 10),
                                                width=LARGEUR_ENTRY, relief="solid", bd=1, show="•")
        self.entry_password_confirm.grid(row=4, column=1, sticky="ew", pady=8, ipady=4)

        self.bouton_valider = tk.Button(
            self.carte, text="✅ Enregistrer les modifications", font=Theme.FONT_SUBTITLE,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            activebackground=Theme.PRIMARY_DARK, activeforeground="white",
            command=self._valider
        )
        self.bouton_valider.grid(row=5, column=0, columnspan=2, sticky="ew",
                                  pady=(20, 0), ipady=8)

        self.carte.grid_columnconfigure(1, weight=1)

    def on_afficher(self):
        """Pre-remplit le formulaire avec les donnees actuelles de l'utilisateur."""
        user_id = self.app_state.get("utilisateur_id")
        if user_id is None or not self.db.is_connected():
            return

        user = self.db.obtenir_utilisateur_par_id(user_id)
        if user is None:
            return

        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, user["nom_utilisateur"])

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, user["email"])

        self.entry_password.delete(0, tk.END)
        self.entry_password_confirm.delete(0, tk.END)

    def _valider(self):
        nom_utilisateur = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        password_confirm = self.entry_password_confirm.get()

        if not nom_utilisateur or not email:
            messagebox.showwarning("Champs requis", "Le nom d'utilisateur et l'email sont obligatoires.")
            return

        if password or password_confirm:
            if password != password_confirm:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
                return
            if len(password) < 6:
                messagebox.showwarning(
                    "Mot de passe trop court",
                    "Le mot de passe doit contenir au moins 6 caractères."
                )
                return

        user_id = self.app_state.get("utilisateur_id")
        if not self.db.is_connected():
            messagebox.showerror("MySQL", "Non connecté à la base de données.")
            return

        succes, message = self.db.modifier_utilisateur(
            user_id,
            nom_utilisateur=nom_utilisateur,
            email=email,
            nouveau_password=password if password else None,
        )

        if succes:
            messagebox.showinfo("Profil", message)
            self.entry_password.delete(0, tk.END)
            self.entry_password_confirm.delete(0, tk.END)
            if self.on_profil_modifie:
                self.on_profil_modifie(nom_utilisateur)
        else:
            messagebox.showerror("Erreur", message)

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        c = Theme.get(mode_theme)

        self.config(bg=c["bg"])
        self.label_titre.config(bg=c["bg"], fg=Theme.PRIMARY)
        self.label_sous_titre.config(bg=c["bg"], fg=c["subtext"])
        self.carte.config(bg=c["card"], highlightbackground=c["border"])
        self.label_separateur.config(bg=c["card"], fg=c["subtext"])

        for lbl in (self.label_username, self.label_email,
                    self.label_password, self.label_password_confirm):
            lbl.config(bg=c["card"], fg=c["text"])