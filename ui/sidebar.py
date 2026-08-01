"""
Date : 01/08/2026
Auteur : Elpidio Alexis AMOUSSOU
Email : amoussouelpidioalexis@gmail.com

"""
# -*- coding: utf-8 -*-
"""
ui/sidebar.py
Barre laterale de navigation, pliable (mode hamburger), avec bascule
clair/sombre reflechie dans le libelle du bouton.
"""

import tkinter as tk
from config import Theme


class Sidebar(tk.Frame):
    LARGEUR_DEPLIEE = 230
    LARGEUR_PLIEE = 60

    ITEMS = [
        ("inventaire", "📦", "Inventaire Équipements"),
        ("parametres", "🏙️", "Paramètres du Projet"),
        ("bom", "📋", "BOM & Devis"),
        ("historique", "🕓", "Historique"),
        ("profil", "👤", "Mon Profil"),
    ]

    def __init__(self, master, utilisateur, on_navigate, on_toggle_theme,
                 on_logout, mode_theme="clair"):
        super().__init__(master, width=self.LARGEUR_DEPLIEE)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme
        self.on_logout = on_logout
        self.mode_theme = mode_theme
        self.repliee = False
        self.utilisateur = utilisateur

        self.boutons_nav = {}
        self.widgets_texte = []

        self._construire_interface()
        self.appliquer_theme(self.mode_theme)

    # --------------------------------------------------------
    def _construire_interface(self):
        barre_hamburger = tk.Frame(self, height=44)
        barre_hamburger.pack(fill="x")
        barre_hamburger.pack_propagate(False)
        self.bouton_hamburger = tk.Button(
            barre_hamburger, text="☰", font=(Theme.FONT_FAMILY, 14, "bold"),
            relief="flat", bd=0, cursor="hand2",
            command=self._basculer_pliage
        )
        self.bouton_hamburger.pack(side="left", padx=10, pady=8)
        self.barre_hamburger = barre_hamburger

        self.entete = tk.Frame(self, bg=Theme.PRIMARY, height=80)
        self.entete.pack(fill="x")
        self.entete.pack_propagate(False)
        self.label_logo = tk.Label(
            self.entete, text="⚡ FiberSim", font=(Theme.FONT_FAMILY, 15, "bold"),
            bg=Theme.PRIMARY, fg="white"
        )
        self.label_logo.pack(pady=(16, 0))
        self.label_user = tk.Label(
            self.entete, text=f"Connecté : {self.utilisateur['nom_utilisateur']}",
            font=Theme.FONT_SMALL, bg=Theme.PRIMARY, fg=Theme.PRIMARY_LIGHT
        )
        self.label_user.pack()
        self.widgets_texte.append(self.label_user)

        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(fill="x", pady=16)

        for cle, icone, label in self.ITEMS:
            btn = tk.Button(
                self.nav_frame, text=f"{icone}  {label}", font=Theme.FONT_NORMAL,
                anchor="w", relief="flat", bd=0, padx=18, pady=12, cursor="hand2",
                command=lambda c=cle: self._naviguer(c)
            )
            btn.pack(fill="x")
            self.boutons_nav[cle] = (btn, icone, label)

        self.bas_frame = tk.Frame(self)
        self.bas_frame.pack(side="bottom", fill="x", pady=16)

        self.bouton_theme = tk.Button(
            self.bas_frame, text="🌙  Mode sombre", font=Theme.FONT_SMALL,
            relief="flat", cursor="hand2", anchor="w", padx=18,
            command=self._basculer_theme_direct
        )
        self.bouton_theme.pack(fill="x", pady=(0, 6))

        self.bouton_logout = tk.Button(
            self.bas_frame, text="🚪  Déconnexion", font=Theme.FONT_SMALL,
            fg=Theme.DANGER, relief="flat", cursor="hand2", anchor="w", padx=18,
            command=self.on_logout
        )
        self.bouton_logout.pack(fill="x")

    # --------------------------------------------------------
    def _naviguer(self, cle):
        for k, (btn, icone, label) in self.boutons_nav.items():
            couleurs = Theme.get(self.mode_theme)
            if k == cle:
                btn.config(bg=Theme.PRIMARY, fg="white")
            else:
                btn.config(bg=couleurs["sidebar"], fg=couleurs["text"])
        self.on_navigate(cle)

    def selectionner(self, cle):
        self._naviguer(cle)

    def mettre_a_jour_nom_utilisateur(self, nouveau_nom):
        self.utilisateur["nom_utilisateur"] = nouveau_nom
        if not self.repliee:
            self.label_user.config(text=f"Connecté : {nouveau_nom}")

    # --------------------------------------------------------
    def _basculer_pliage(self):
        self.repliee = not self.repliee
        if self.repliee:
            self.config(width=self.LARGEUR_PLIEE)
            self.label_logo.config(text="⚡")
            for widget in self.widgets_texte:
                widget.pack_forget()
            for cle, (btn, icone, label) in self.boutons_nav.items():
                btn.config(text=icone)
            self.bouton_theme.config(
                text="🌙" if self.mode_theme == "clair" else "☀️"
            )
            self.bouton_logout.config(text="🚪")
        else:
            self.config(width=self.LARGEUR_DEPLIEE)
            self.label_logo.config(text="⚡ FiberSim")
            self.label_user.pack()
            for cle, (btn, icone, label) in self.boutons_nav.items():
                btn.config(text=f"{icone}  {label}")
            self._mettre_a_jour_bouton_theme()
            self.bouton_logout.config(text="🚪  Déconnexion")

    # --------------------------------------------------------
    def _basculer_theme_direct(self):
        self.on_toggle_theme()

    def _mettre_a_jour_bouton_theme(self):
        if self.mode_theme == "clair":
            self.bouton_theme.config(
                text="🌙" if self.repliee else "🌙  Mode sombre"
            )
        else:
            self.bouton_theme.config(
                text="☀️" if self.repliee else "☀️  Mode clair"
            )

    # --------------------------------------------------------
    def appliquer_theme(self, mode_theme):
        self.mode_theme = mode_theme
        couleurs = Theme.get(mode_theme)

        self.config(bg=couleurs["sidebar"])
        self.barre_hamburger.config(bg=couleurs["sidebar"])
        self.bouton_hamburger.config(bg=couleurs["sidebar"], fg=couleurs["text"],
                                      activebackground=couleurs["border"])
        self.nav_frame.config(bg=couleurs["sidebar"])
        self.bas_frame.config(bg=couleurs["sidebar"])
        self.label_user.config(bg=Theme.PRIMARY)

        for cle, (btn, icone, label) in self.boutons_nav.items():
            btn.config(bg=couleurs["sidebar"], fg=couleurs["text"],
                       activebackground=couleurs["border"],
                       activeforeground=couleurs["text"])

        self.bouton_theme.config(bg=couleurs["sidebar"], fg=couleurs["subtext"],
                                  activebackground=couleurs["border"])
        self.bouton_logout.config(bg=couleurs["sidebar"],
                                   activebackground=couleurs["border"])

        self._mettre_a_jour_bouton_theme()