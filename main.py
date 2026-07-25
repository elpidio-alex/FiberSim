# -*- coding: utf-8 -*-
"""
main.py
Point d'entree de FiberSim : authentification, fenetre principale,
navigation, bascule clair/sombre globale.
"""

import tkinter as tk
from tkinter import messagebox

from config import Theme, Paths
from database import Database
from equipment_manager import EquipmentManager
from bom_calculator import BOMCalculator
from export_manager import ExportManager

from ui.login_frame import LoginFrame
from ui.sidebar import Sidebar
from ui.inventory_frame import InventoryFrame
from ui.project_params_frame import ProjectParamsFrame
from ui.bom_frame import BOMFrame
from ui.history_frame import HistoryFrame
from ui.profile_frame import ProfileFrame


class FiberSimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FiberSim — Simulation et Optimisation Réseau FO Urbain")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Icone de la fenetre (si le fichier logo.ico est present)
        try:
            self.iconbitmap(Paths.LOGO_ICO)
        except tk.TclError:
            pass  # icone absente ou format non supporte, on continue sans

        Paths.ensure_dirs()

        self.db = Database()
        self.equipment_manager = EquipmentManager()  # aucun fichier par defaut
        self.bom_calculator = BOMCalculator(self.equipment_manager)
        self.export_manager = ExportManager()

        self.app_state = {}
        self.mode_theme = "clair"

        self.sidebar = None
        self.zone_contenu = None
        self.frames = {}

        self._demarrer_connexion_bd()
        self._afficher_login()

    # --------------------------------------------------------
    def _demarrer_connexion_bd(self):
        if not self.db.connect():
            messagebox.showwarning(
                "Base de données",
                "Connexion MySQL impossible. L'historique des devis et la "
                "gestion du profil seront indisponibles, mais vous pouvez "
                "continuer à utiliser l'inventaire, le BOM et les exports."
            )

    # --------------------------------------------------------
    def _afficher_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(bg=Theme.LIGHT_BG)
        self.login_frame = LoginFrame(self, self.db, self._on_login_success)
        self.login_frame.pack(fill="both", expand=True)

    def _on_login_success(self, utilisateur):
        self.app_state["utilisateur_id"] = utilisateur["id"]
        self.login_frame.destroy()
        self._construire_interface_principale(utilisateur)

    # --------------------------------------------------------
    def _construire_interface_principale(self, utilisateur):
        self.conteneur_principal = tk.Frame(self)
        self.conteneur_principal.pack(fill="both", expand=True)

        self.sidebar = Sidebar(
            self.conteneur_principal, utilisateur,
            on_navigate=self._naviguer,
            on_toggle_theme=self._basculer_theme,
            on_logout=self._deconnexion,
            mode_theme=self.mode_theme,
        )
        self.sidebar.pack(side="left", fill="y")

        self.zone_contenu = tk.Frame(self.conteneur_principal)
        self.zone_contenu.pack(side="left", fill="both", expand=True)

        self.frames["inventaire"] = InventoryFrame(
            self.zone_contenu, self.equipment_manager, self.app_state
        )
        self.frames["parametres"] = ProjectParamsFrame(
            self.zone_contenu, self.app_state,
            on_params_valides=lambda: self._naviguer("bom")
        )
        self.frames["bom"] = BOMFrame(
            self.zone_contenu, self.bom_calculator, self.export_manager,
            self.db, self.app_state, self.frames["inventaire"]
        )
        self.frames["historique"] = HistoryFrame(self.zone_contenu, self.db)
        self.frames["profil"] = ProfileFrame(
            self.zone_contenu, self.db, self.app_state,
            on_profil_modifie=self._on_profil_modifie
        )

        for frame in self.frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._appliquer_theme_global()
        self._naviguer("inventaire")
        self.sidebar.selectionner("inventaire")

    def _naviguer(self, cle):
        frame = self.frames.get(cle)
        if frame is None:
            return
        frame.tkraise()
        if hasattr(frame, "on_afficher"):
            frame.on_afficher()

    def _on_profil_modifie(self, nouveau_nom):
        """Met a jour l'affichage du nom d'utilisateur dans la sidebar."""
        self.sidebar.mettre_a_jour_nom_utilisateur(nouveau_nom)

    # --------------------------------------------------------
    def _basculer_theme(self):
        self.mode_theme = "sombre" if self.mode_theme == "clair" else "clair"
        self._appliquer_theme_global()

    def _appliquer_theme_global(self):
        c = Theme.get(self.mode_theme)
        self.configure(bg=c["bg"])
        self.conteneur_principal.config(bg=c["bg"])
        self.zone_contenu.config(bg=c["bg"])

        self.sidebar.appliquer_theme(self.mode_theme)

        for frame in self.frames.values():
            if hasattr(frame, "appliquer_theme"):
                frame.appliquer_theme(self.mode_theme)

    # --------------------------------------------------------
    def _deconnexion(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.app_state.clear()
            for widget in self.winfo_children():
                widget.destroy()
            self._afficher_login()

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = FiberSimApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()