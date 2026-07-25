# -*- coding: utf-8 -*-
"""
ui/login_frame.py
Ecran de connexion et de creation de compte utilisateur (avec email).
Champs alignes via grid() pour garantir une largeur identique.
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme


class LoginFrame(tk.Frame):
    LARGEUR_ENTRY = 32  # largeur identique pour tous les champs

    def __init__(self, master, db, on_login_success):
        super().__init__(master, bg=Theme.LIGHT_BG)
        self.db = db
        self.on_login_success = on_login_success
        self.mode_creation = tk.BooleanVar(value=False)

        self._construire_interface()

    def _construire_interface(self):
        self.conteneur = tk.Frame(self, bg=Theme.LIGHT_CARD, padx=40, pady=40,
                                   highlightbackground=Theme.LIGHT_BORDER,
                                   highlightthickness=1)
        self.conteneur.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.conteneur, text="FiberSim", font=(Theme.FONT_FAMILY, 26, "bold"),
            fg=Theme.PRIMARY, bg=Theme.LIGHT_CARD
        ).grid(row=0, column=0, pady=(0, 4), sticky="w")

        tk.Label(
            self.conteneur, text="Simulation et Optimisation Réseau FO Urbain",
            font=Theme.FONT_SMALL, fg=Theme.LIGHT_SUBTEXT, bg=Theme.LIGHT_CARD
        ).grid(row=1, column=0, pady=(0, 24), sticky="w")

        # Champ nom d'utilisateur
        self.label_username = tk.Label(
            self.conteneur, text="Nom d'utilisateur", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_TEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.label_username.grid(row=2, column=0, sticky="w")
        self.entry_username = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="solid", bd=1
        )
        self.entry_username.grid(row=3, column=0, pady=(4, 14), ipady=5, sticky="ew")

        # Champ email (visible uniquement en mode creation)
        self.label_email = tk.Label(
            self.conteneur, text="Adresse email", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_TEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.entry_email = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="solid", bd=1
        )

        # Champ mot de passe
        self.label_password = tk.Label(
            self.conteneur, text="Mot de passe", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_TEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.label_password.grid(row=6, column=0, sticky="w")
        self.entry_password = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="solid", bd=1, show="•"
        )
        self.entry_password.grid(row=7, column=0, pady=(4, 20), ipady=5, sticky="ew")

        # Bouton principal
        self.bouton_action = tk.Button(
            self.conteneur, text="Se connecter", font=Theme.FONT_SUBTITLE,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            activebackground=Theme.PRIMARY_DARK, activeforeground="white",
            command=self._soumettre
        )
        self.bouton_action.grid(row=8, column=0, ipady=8, pady=(0, 10), sticky="ew")

        # Lien bascule connexion / creation
        self.lien_bascule = tk.Label(
            self.conteneur, text="Pas encore de compte ? Créer un compte",
            font=Theme.FONT_SMALL, fg=Theme.ACCENT_DARK, bg=Theme.LIGHT_CARD,
            cursor="hand2"
        )
        self.lien_bascule.grid(row=9, column=0)
        self.lien_bascule.bind("<Button-1>", lambda e: self._basculer_mode())

        self.conteneur.grid_columnconfigure(0, weight=1)

        self.entry_password.bind("<Return>", lambda e: self._soumettre())

    def _basculer_mode(self):
        self.mode_creation.set(not self.mode_creation.get())
        if self.mode_creation.get():
            # Champ email insere entre username (row 3) et password (row 6)
            self.label_email.grid(row=4, column=0, sticky="w")
            self.entry_email.grid(row=5, column=0, pady=(4, 14), ipady=5, sticky="ew")
            self.bouton_action.config(text="Créer le compte")
            self.lien_bascule.config(text="Déjà un compte ? Se connecter")
        else:
            self.label_email.grid_forget()
            self.entry_email.grid_forget()
            self.bouton_action.config(text="Se connecter")
            self.lien_bascule.config(text="Pas encore de compte ? Créer un compte")

    def _soumettre(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs.")
            return

        if self.mode_creation.get():
            email = self.entry_email.get().strip()
            if not email:
                messagebox.showwarning("Champ requis", "Veuillez renseigner votre email.")
                return
            succes, message = self.db.creer_utilisateur(username, email, password)
            if succes:
                messagebox.showinfo("Succès", message)
                self._basculer_mode()
            else:
                messagebox.showerror("Erreur", message)
        else:
            succes, user = self.db.verifier_utilisateur(username, password)
            if succes:
                self.on_login_success(user)
            else:
                messagebox.showerror("Échec", "Nom d'utilisateur ou mot de passe incorrect.")