# -*- coding: utf-8 -*-
"""
ui/login_frame.py
Ecran de connexion et de creation de compte utilisateur.
Panneau lateral avec degrade Violet -> Ambre et illustration reseau
vectorielle, carte de connexion blanche centree a droite.
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme


def _hex_vers_rgb(couleur_hex):
    couleur_hex = couleur_hex.lstrip("#")
    return tuple(int(couleur_hex[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_vers_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _interpoler_couleur(couleur1, couleur2, ratio):
    r1, g1, b1 = _hex_vers_rgb(couleur1)
    r2, g2, b2 = _hex_vers_rgb(couleur2)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return _rgb_vers_hex((r, g, b))


class LoginFrame(tk.Frame):
    LARGEUR_ENTRY = 32
    LARGEUR_PANNEAU_RATIO = 0.4  # 40% de la largeur pour le panneau colore

    def __init__(self, master, db, on_login_success):
        super().__init__(master, bg=Theme.LIGHT_BG)
        self.db = db
        self.on_login_success = on_login_success
        self.mode_creation = tk.BooleanVar(value=False)

        self._construire_interface()
        self.bind("<Configure>", self._on_resize)

    # --------------------------------------------------------
    def _construire_interface(self):
        # Panneau lateral colore (degrade + illustration)
        self.canvas_panneau = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas_panneau.place(relx=0, rely=0, relwidth=self.LARGEUR_PANNEAU_RATIO,
                                   relheight=1)

        # Carte de connexion blanche, centree dans la zone restante
        self.conteneur = tk.Frame(self, bg=Theme.LIGHT_CARD, padx=44, pady=40,
                                   highlightbackground=Theme.LIGHT_BORDER,
                                   highlightthickness=1)
        self._positionner_carte()

        self._construire_formulaire()

    def _positionner_carte(self):
        """Centre la carte dans la zone a droite du panneau colore."""
        centre_x = self.LARGEUR_PANNEAU_RATIO + (1 - self.LARGEUR_PANNEAU_RATIO) / 2
        self.conteneur.place(relx=centre_x, rely=0.5, anchor="center")

    def _on_resize(self, event):
        self._redessiner_panneau()

    # --------------------------------------------------------
    # Panneau colore : degrade + illustration vectorielle
    # --------------------------------------------------------
    def _redessiner_panneau(self):
        self.canvas_panneau.delete("all")
        largeur = self.canvas_panneau.winfo_width()
        hauteur = self.canvas_panneau.winfo_height()
        if largeur <= 1 or hauteur <= 1:
            return

        self._dessiner_degrade(largeur, hauteur)
        self._dessiner_illustration_reseau(largeur, hauteur)
        self._dessiner_texte_logo(largeur, hauteur)

    def _dessiner_degrade(self, largeur, hauteur):
        """Degrade vertical Violet (haut) -> Ambre (bas)."""
        pas = 2  # dessiner par bandes de 2px pour la performance
        for y in range(0, hauteur, pas):
            ratio = y / hauteur
            couleur = _interpoler_couleur(Theme.PRIMARY, Theme.ACCENT, ratio)
            self.canvas_panneau.create_rectangle(
                0, y, largeur, y + pas, fill=couleur, outline=couleur
            )

    def _dessiner_illustration_reseau(self, largeur, hauteur):
        """Illustration vectorielle : noeuds connectes façon reseau FO."""
        import random
        random.seed(42)  # motif stable a chaque redessin

        centre_x = largeur / 2
        centre_y = hauteur * 0.38
        rayon_zone = min(largeur, hauteur) * 0.22

        noeuds = []
        nb_noeuds = 7
        for i in range(nb_noeuds):
            angle = (2 * 3.14159 * i / nb_noeuds) + random.uniform(-0.3, 0.3)
            distance = rayon_zone * random.uniform(0.4, 1.0)
            x = centre_x + distance * __import__("math").cos(angle)
            y = centre_y + distance * __import__("math").sin(angle)
            noeuds.append((x, y))
        noeuds.append((centre_x, centre_y))  # noeud central

        couleur_ligne = "#FFFFFF"

        # Lignes de connexion (chaque noeud relie au centre + quelques voisins)
        for i, (x, y) in enumerate(noeuds[:-1]):
            self.canvas_panneau.create_line(
                x, y, centre_x, centre_y, fill=couleur_ligne, width=1.5,
                stipple="gray50"
            )
            if i > 0:
                x_prec, y_prec = noeuds[i - 1]
                self.canvas_panneau.create_line(
                    x, y, x_prec, y_prec, fill=couleur_ligne, width=1,
                    stipple="gray25"
                )

        # Points (noeuds), le central plus gros
        for i, (x, y) in enumerate(noeuds):
            rayon_pt = 7 if i == len(noeuds) - 1 else 4
            self.canvas_panneau.create_oval(
                x - rayon_pt, y - rayon_pt, x + rayon_pt, y + rayon_pt,
                fill="#FFFFFF", outline="#FFFFFF"
            )
            self.canvas_panneau.create_oval(
                x - rayon_pt + 2, y - rayon_pt + 2, x + rayon_pt - 2, y + rayon_pt - 2,
                fill=Theme.PRIMARY_DARK, outline=""
            )

    def _dessiner_texte_logo(self, largeur, hauteur):
        centre_x = largeur / 2
        y_logo = hauteur * 0.60

        logo_affiche = self._afficher_logo_image(centre_x, y_logo)

        y_nom = hauteur * 0.68 if logo_affiche else hauteur * 0.60

        self.canvas_panneau.create_text(
            centre_x, y_nom, text="⚡ FiberSim" if not logo_affiche else "FiberSim",
            font=(Theme.FONT_FAMILY, 26, "bold"), fill="white"
        )
        self.canvas_panneau.create_text(
            centre_x, y_nom + 34, text="Simulation et Optimisation",
            font=(Theme.FONT_FAMILY, 12), fill="#F5F3FF"
        )
        self.canvas_panneau.create_text(
            centre_x, y_nom + 56, text="Réseau FO Urbain",
            font=(Theme.FONT_FAMILY, 12, "italic"), fill="#F5F3FF"
        )

    def _afficher_logo_image(self, centre_x, y_logo):
        """
        Tente d'afficher assets/logo.png dans le panneau. Retourne True
        si le logo a ete affiche, False si le fichier est absent (repli
        silencieux sur le texte seul).
        """
        from config import Paths
        import os

        if not os.path.exists(Paths.LOGO_PNG):
            return False

        try:
            from PIL import Image, ImageTk

            if not hasattr(self, "_image_logo_cache"):
                image = Image.open(Paths.LOGO_PNG)
                image.thumbnail((90, 90))  # redimensionnement proportionnel
                self._image_logo_cache = ImageTk.PhotoImage(image)

            self.canvas_panneau.create_image(
                centre_x, y_logo, image=self._image_logo_cache
            )
            return True
        except Exception:
            return False  # Pillow absent ou fichier corrompu -> repli texte

    # --------------------------------------------------------
    # Formulaire (carte blanche)
    # --------------------------------------------------------
    def _construire_formulaire(self):
        tk.Label(
            self.conteneur, text="Connexion", font=(Theme.FONT_FAMILY, 22, "bold"),
            fg=Theme.LIGHT_TEXT, bg=Theme.LIGHT_CARD
        ).grid(row=0, column=0, pady=(0, 24), sticky="w")

        # Champ nom d'utilisateur
        self.label_username = tk.Label(
            self.conteneur, text="Nom d'utilisateur", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_SUBTEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.label_username.grid(row=1, column=0, sticky="w")
        self.entry_username = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="flat", bd=0, bg="#F3F4F6", insertbackground=Theme.LIGHT_TEXT
        )
        self.entry_username.grid(row=2, column=0, pady=(4, 16), ipady=8, sticky="ew")

        # Champ email (visible uniquement en mode creation)
        self.label_email = tk.Label(
            self.conteneur, text="Adresse email", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_SUBTEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.entry_email = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="flat", bd=0, bg="#F3F4F6", insertbackground=Theme.LIGHT_TEXT
        )

        # Champ mot de passe
        self.label_password = tk.Label(
            self.conteneur, text="Mot de passe", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_SUBTEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.label_password.grid(row=5, column=0, sticky="w")
        self.entry_password = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="flat", bd=0, bg="#F3F4F6", show="•",
            insertbackground=Theme.LIGHT_TEXT
        )
        self.entry_password.grid(row=6, column=0, pady=(4, 24), ipady=8, sticky="ew")

        # Bouton principal
        self.bouton_action = tk.Button(
            self.conteneur, text="Se connecter", font=Theme.FONT_SUBTITLE,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            activebackground=Theme.PRIMARY_DARK, activeforeground="white",
            command=self._soumettre
        )
        self.bouton_action.grid(row=7, column=0, ipady=10, pady=(0, 14), sticky="ew")

        # Lien bascule connexion / creation
        self.lien_bascule = tk.Label(
            self.conteneur, text="Pas encore de compte ?  Créer un compte",
            font=Theme.FONT_SMALL, fg=Theme.PRIMARY, bg=Theme.LIGHT_CARD,
            cursor="hand2"
        )
        self.lien_bascule.grid(row=8, column=0)
        self.lien_bascule.bind("<Button-1>", lambda e: self._basculer_mode())

        self.conteneur.grid_columnconfigure(0, weight=1)

        self.entry_password.bind("<Return>", lambda e: self._soumettre())

    def _basculer_mode(self):
        self.mode_creation.set(not self.mode_creation.get())
        if self.mode_creation.get():
            self.label_email.grid(row=3, column=0, sticky="w")
            self.entry_email.grid(row=4, column=0, pady=(4, 16), ipady=8, sticky="ew")
            self.bouton_action.config(text="Créer le compte")
            self.lien_bascule.config(text="Déjà un compte ?  Se connecter")
        else:
            self.label_email.grid_forget()
            self.entry_email.grid_forget()
            self.bouton_action.config(text="Se connecter")
            self.lien_bascule.config(text="Pas encore de compte ?  Créer un compte")

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