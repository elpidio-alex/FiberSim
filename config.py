# -*- coding: utf-8 -*-
"""
config.py
Configuration globale : couleurs du theme, constantes MySQL, chemins.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================================
# THEME VISUEL (Violet / Ambre) - Clair & Sombre
# ============================================================
class Theme:
    PRIMARY = "#7C3AED"
    PRIMARY_DARK = "#5B21B6"
    PRIMARY_LIGHT = "#A78BFA"
    ACCENT = "#F59E0B"
    ACCENT_DARK = "#B45309"
    ACCENT_LIGHT = "#FCD34D"

    LIGHT_BG = "#F5F3FF"
    LIGHT_SIDEBAR = "#FFFFFF"
    LIGHT_CARD = "#FFFFFF"
    LIGHT_TEXT = "#1F2937"
    LIGHT_SUBTEXT = "#6B7280"
    LIGHT_BORDER = "#E5E7EB"

    DARK_BG = "#111827"
    DARK_SIDEBAR = "#1F2937"
    DARK_CARD = "#1F2937"
    DARK_TEXT = "#F9FAFB"
    DARK_SUBTEXT = "#9CA3AF"
    DARK_BORDER = "#374151"

    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    WARNING = "#F59E0B"
    INFO = "#3B82F6"

    FONT_FAMILY = "Times New Roman"
    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
    FONT_NORMAL = (FONT_FAMILY, 11)
    FONT_SMALL = (FONT_FAMILY, 10)

    @staticmethod
    def get(mode="clair"):
        """
        Retourne un dict de couleurs actives selon le mode ('clair' ou 'sombre').
        """
        if mode == "sombre":
            return {
                "bg": Theme.DARK_BG,
                "sidebar": Theme.DARK_SIDEBAR,
                "card": Theme.DARK_CARD,
                "text": Theme.DARK_TEXT,
                "subtext": Theme.DARK_SUBTEXT,
                "border": Theme.DARK_BORDER,
            }
        return {
            "bg": Theme.LIGHT_BG,
            "sidebar": Theme.LIGHT_SIDEBAR,
            "card": Theme.LIGHT_CARD,
            "text": Theme.LIGHT_TEXT,
            "subtext": Theme.LIGHT_SUBTEXT,
            "border": Theme.LIGHT_BORDER,
        }


# ============================================================
# BASE DE DONNEES MYSQL
# ============================================================
class DBConfig:
    HOST = os.environ.get("FIBERSIM_DB_HOST", "localhost")
    PORT = int(os.environ.get("FIBERSIM_DB_PORT", 3306))
    USER = os.environ.get("FIBERSIM_DB_USER", "root")
    PASSWORD = os.environ.get("FIBERSIM_DB_PASSWORD", "")
    DATABASE = os.environ.get("FIBERSIM_DB_NAME", "fibersim_db")


# ============================================================
# CHEMINS ET FICHIERS
# ============================================================
class Paths:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LISTE_XLSX = os.path.join(BASE_DIR, "Liste.xlsx")
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

    @staticmethod
    def ensure_dirs():
        os.makedirs(Paths.EXPORTS_DIR, exist_ok=True)
        os.makedirs(Paths.ASSETS_DIR, exist_ok=True)


# ============================================================
# CONSTANTES METIER (algorithmes de couverture / quantification)
# ============================================================
class NetworkParams:
    RAYON_COUVERTURE_ANTENNE = 0.6
    HABITANTS_PAR_CELLULE = 2500
    TAUX_PENETRATION_FTTH = 0.35
    CABLE_ML_PAR_KM2 = 1200
    CHAMBRES_PAR_KM_CABLE = 4
    RATIO_FOURREAU_CABLE = 1.0
    BPE_PAR_ML_CABLE = 1 / 500
    ONT_PAR_OLT = 128 * 16
    TAUX_TVA = 0.18