# =============================================================
# generate_ico.py — Génération de l'icône NetSentinel
# Convertit le logo PNG en fichier .ico multi-résolutions
# pour la fenêtre Tkinter et la barre des tâches Windows.
# =============================================================
# Utilisation :
#   Placez ce script à la racine du projet (même dossier que main.py)
#   Placez le logo dans assets/logo.png
#   python generate_ico.py
# =============================================================

from PIL import Image
import os

LOGO_SOURCE = "assets/logo.png"
ICO_SORTIE  = "assets/netsentinel.ico"

# Tailles requises pour un .ico Windows complet
TAILLES = [16, 24, 32, 48, 64, 128, 256]


def generer_ico():
    if not os.path.exists(LOGO_SOURCE):
        print(f"❌ Logo introuvable : {LOGO_SOURCE}")
        print("   Placez votre logo PNG dans assets/logo.png et relancez.")
        return

    os.makedirs("assets", exist_ok=True)

    img = Image.open(LOGO_SOURCE).convert("RGBA")

    images = []
    for taille in TAILLES:
        redimensionnee = img.resize((taille, taille), Image.LANCZOS)
        images.append(redimensionnee)

    images[0].save(
        ICO_SORTIE,
        format="ICO",
        sizes=[(t, t) for t in TAILLES],
        append_images=images[1:]
    )

    print(f"✅ Icône générée : {ICO_SORTIE}")
    print(f"   Résolutions incluses : {', '.join(str(t) for t in TAILLES)}px")


if __name__ == "__main__":
    generer_ico()
