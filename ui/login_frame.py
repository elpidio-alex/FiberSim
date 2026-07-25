# -*- coding: utf-8 -*-
"""
ui/login_frame.py
Ecran de connexion et de creation de compte utilisateur.
Panneau lateral avec degrade Violet -> Ambre (pre-rendu via Pillow) et
logo, carte de connexion blanche centree a droite.
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme, Paths


def _hex_vers_rgb(couleur_hex):
    couleur_hex = couleur_hex.lstrip("#")
    return tuple(int(couleur_hex[i:i + 2], 16) for i in (0, 2, 4))


class LoginFrame(tk.Frame):
    LARGEUR_ENTRY = 32
    LARGEUR_PANNEAU_RATIO = 0.4

    def __init__(self, master, db, on_login_success):
        super().__init__(master, bg=Theme.LIGHT_BG)
        self.db = db
        self.on_login_success = on_login_success
        self.mode_creation = tk.BooleanVar(value=False)

        self._image_degrade_cache = None
        self._image_logo_cache = None
        self._derniere_taille = (0, 0)

        self._construire_interface()
        self.bind("<Configure>", self._on_resize)

    # --------------------------------------------------------
    def _construire_interface(self):
        self.canvas_panneau = tk.Canvas(self, highlightthickness=0, bd=0,
                                         bg=Theme.PRIMARY)
        self.canvas_panneau.place(relx=0, rely=0, relwidth=self.LARGEUR_PANNEAU_RATIO,
                                   relheight=1)

        self.conteneur = tk.Frame(self, bg=Theme.LIGHT_CARD, padx=44, pady=40,
                                   highlightbackground=Theme.LIGHT_BORDER,
                                   highlightthickness=1)

        self._construire_formulaire()

    def _on_resize(self, event):
        largeur = self.winfo_width()
        hauteur = self.winfo_height()

        # Ne redessiner que si la taille a reellement change (evite le
        # redessin en boucle a chaque micro-evenement Configure)
        if (largeur, hauteur) == self._derniere_taille or largeur <= 1:
            return
        self._derniere_taille = (largeur, hauteur)

        self._redessiner_panneau()
        self._positionner_carte()

    # --------------------------------------------------------
    # Panneau colore : degrade pre-rendu (Pillow) + logo
    # --------------------------------------------------------
    def _redessiner_panneau(self):
        largeur_totale = self.winfo_width()
        hauteur_totale = self.winfo_height()
        largeur_panneau = max(1, int(largeur_totale * self.LARGEUR_PANNEAU_RATIO))

        self.canvas_panneau.config(width=largeur_panneau, height=hauteur_totale)
        self.canvas_panneau.delete("all")

        self._dessiner_degrade_image(largeur_panneau, hauteur_totale)
        self._dessiner_texte_logo(largeur_panneau, hauteur_totale)

    def _dessiner_degrade_image(self, largeur, hauteur):
        """Genere le degrade une seule fois en image Pillow (rapide),
        au lieu de centaines de create_rectangle un par un."""
        try:
            from PIL import Image, ImageTk
        except ImportError:
            # Repli si Pillow indisponible : couleur unie
            self.canvas_panneau.create_rectangle(
                0, 0, largeur, hauteur, fill=Theme.PRIMARY, outline=Theme.PRIMARY
            )
            return

        couleur1 = _hex_vers_rgb(Theme.PRIMARY)
        couleur2 = _hex_vers_rgb(Theme.ACCENT)

        # Degrade calcule sur une bande de 1px de large, puis etiree
        degrade = Image.new("RGB", (1, hauteur))
        pixels = degrade.load()
        for y in range(hauteur):
            ratio = y / hauteur if hauteur else 0
            r = int(couleur1[0] + (couleur2[0] - couleur1[0]) * ratio)
            g = int(couleur1[1] + (couleur2[1] - couleur1[1]) * ratio)
            b = int(couleur1[2] + (couleur2[2] - couleur1[2]) * ratio)
            pixels[0, y] = (r, g, b)

        degrade = degrade.resize((largeur, hauteur))
        self._image_degrade_cache = ImageTk.PhotoImage(degrade)
        self.canvas_panneau.create_image(0, 0, image=self._image_degrade_cache, anchor="nw")

    def _dessiner_texte_logo(self, largeur, hauteur):
        centre_x = largeur / 2
        y_logo = hauteur * 0.42

        logo_affiche = self._afficher_logo_image(centre_x, y_logo, hauteur)

        y_nom = y_logo + 80 if logo_affiche else hauteur * 0.45

        self.canvas_panneau.create_text(
            centre_x, y_nom, text="FiberSim",
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

    def _afficher_logo_image(self, centre_x, y_logo, hauteur_canvas):
        import os
        if not os.path.exists(Paths.LOGO_PNG):
            return False

        try:
            from PIL import Image, ImageTk

            ratio_y = y_logo / hauteur_canvas if hauteur_canvas else 0.4
            couleur1 = _hex_vers_rgb(Theme.PRIMARY)
            couleur2 = _hex_vers_rgb(Theme.ACCENT)
            couleur_fond = tuple(
                int(couleur1[i] + (couleur2[i] - couleur1[i]) * ratio_y)
                for i in range(3)
            )

            image_originale = Image.open(Paths.LOGO_PNG).convert("RGBA")
            image_originale.thumbnail((90, 90))

            fond = Image.new("RGBA", image_originale.size, couleur_fond + (255,))
            image_composee = Image.alpha_composite(fond, image_originale)

            self._image_logo_cache = ImageTk.PhotoImage(image_composee)
            self.canvas_panneau.create_image(
                centre_x, y_logo, image=self._image_logo_cache
            )
            return True
        except Exception:
            return False

    # --------------------------------------------------------
    def _positionner_carte(self):
        largeur_totale = self.winfo_width()
        if largeur_totale <= 1:
            return

        largeur_panneau = largeur_totale * self.LARGEUR_PANNEAU_RATIO
        largeur_zone_droite = largeur_totale - largeur_panneau
        centre_x_pixels = largeur_panneau + (largeur_zone_droite / 2)

        self.conteneur.place(x=centre_x_pixels, rely=0.5, anchor="center")

    # --------------------------------------------------------
    # Formulaire (carte blanche)
    # --------------------------------------------------------
    def _construire_formulaire(self):
        tk.Label(
            self.conteneur, text="Connexion", font=(Theme.FONT_FAMILY, 22, "bold"),
            fg=Theme.LIGHT_TEXT, bg=Theme.LIGHT_CARD
        ).grid(row=0, column=0, pady=(0, 24), sticky="w")

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

        self.label_email = tk.Label(
            self.conteneur, text="Adresse email", font=Theme.FONT_NORMAL,
            fg=Theme.LIGHT_SUBTEXT, bg=Theme.LIGHT_CARD, anchor="w"
        )
        self.entry_email = tk.Entry(
            self.conteneur, font=("Consolas", 11), width=self.LARGEUR_ENTRY,
            relief="flat", bd=0, bg="#F3F4F6", insertbackground=Theme.LIGHT_TEXT
        )

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

        self.bouton_action = tk.Button(
            self.conteneur, text="Se connecter", font=Theme.FONT_SUBTITLE,
            bg=Theme.PRIMARY, fg="white", relief="flat", cursor="hand2",
            activebackground=Theme.PRIMARY_DARK, activeforeground="white",
            command=self._soumettre
        )
        self.bouton_action.grid(row=7, column=0, ipady=10, pady=(0, 14), sticky="ew")

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