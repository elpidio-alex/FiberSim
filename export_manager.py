# -*- coding: utf-8 -*-
"""
export_manager.py
Export du devis genere (BOM) au format CSV et PDF (reportlab).
"""

import csv
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from config import Paths, Theme


class ExportManager:
    """Genere les fichiers d'export CSV et PDF du devis FiberSim."""

    def __init__(self):
        Paths.ensure_dirs()

    # --------------------------------------------------------
    # Export CSV
    # --------------------------------------------------------
    def exporter_csv(self, nom_projet, bom_resultat, chemin_sortie=None):
        if chemin_sortie is None:
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"devis_{nom_projet.replace(' ', '_')}_{horodatage}.csv"
            chemin_sortie = os.path.join(Paths.EXPORTS_DIR, nom_fichier)

        try:
            with open(chemin_sortie, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Devis FiberSim -", nom_projet])
                writer.writerow(["Date", datetime.now().strftime("%d/%m/%Y %H:%M")])
                writer.writerow(["Population totale", bom_resultat["population_totale"]])
                writer.writerow(["Nombre de cellules estime", bom_resultat["nb_cellules_estime"]])
                writer.writerow([])
                writer.writerow([
                    "ID", "Équipement", "Type", "Quantité",
                    "Prix Unitaire (€)", "Prix Total (€)", "Stock Disponible",
                    "Stock Suffisant"
                ])
                for ligne in bom_resultat["lignes"]:
                    writer.writerow([
                        ligne["equipement_id"],
                        ligne["nom_equipement"],
                        ligne["type"],
                        ligne["quantite"],
                        f"{ligne['prix_unitaire']:.2f}",
                        f"{ligne['prix_total']:.2f}",
                        ligne["stock_disponible"],
                        "Oui" if ligne["stock_suffisant"] else "NON - RUPTURE",
                    ])
                writer.writerow([])
                writer.writerow(["", "", "", "", "Total HT", f"{bom_resultat['cout_total_ht']:.2f}"])
                writer.writerow(["", "", "", "", "TVA (18%)", f"{bom_resultat['cout_tva']:.2f}"])
                writer.writerow(["", "", "", "", "Total TTC", f"{bom_resultat['cout_total_ttc']:.2f}"])

            return True, chemin_sortie
        except Exception as e:
            return False, f"Erreur lors de l'export CSV : {e}"

    # --------------------------------------------------------
    # Export PDF (reportlab)
    # --------------------------------------------------------
    def exporter_pdf(self, nom_projet, bom_resultat, params_projet, chemin_sortie=None):
        """
        params_projet : dict avec surface_km2, densite_habitants, nb_cellules_demande
        """
        if chemin_sortie is None:
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"devis_{nom_projet.replace(' ', '_')}_{horodatage}.pdf"
            chemin_sortie = os.path.join(Paths.EXPORTS_DIR, nom_fichier)

        try:
            doc = SimpleDocTemplate(
                chemin_sortie, pagesize=A4,
                topMargin=15 * mm, bottomMargin=15 * mm,
                leftMargin=15 * mm, rightMargin=15 * mm,
            )
            styles = getSampleStyleSheet()

            style_titre = ParagraphStyle(
                "TitreFiberSim", parent=styles["Title"],
                textColor=colors.HexColor(Theme.PRIMARY), fontSize=20,
            )
            style_soustitre = ParagraphStyle(
                "SousTitre", parent=styles["Normal"],
                textColor=colors.HexColor(Theme.ACCENT_DARK), fontSize=11,
                spaceAfter=4,
            )
            style_normal = styles["Normal"]
            style_section = ParagraphStyle(
                "Section", parent=styles["Heading2"],
                textColor=colors.HexColor(Theme.PRIMARY_DARK), fontSize=13,
                spaceBefore=10, spaceAfter=6,
            )

            elements = []

            elements.append(Paragraph("FiberSim — Devis de Déploiement FO", style_titre))
            elements.append(Paragraph(f"Projet : {nom_projet}", style_soustitre))
            elements.append(Paragraph(
                f"Date d'émission : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                style_normal
            ))
            elements.append(Spacer(1, 10))

            # Section parametres du projet
            elements.append(Paragraph("Paramètres du Projet Urbain", style_section))
            data_params = [
                ["Surface couverte", f"{params_projet['surface_km2']} km²"],
                ["Densité de population", f"{params_projet['densite_habitants']} hab/km²"],
                ["Population totale estimée", f"{bom_resultat['population_totale']} habitants"],
                ["Nombre de cellules estimé", str(bom_resultat['nb_cellules_estime'])],
            ]
            table_params = Table(data_params, colWidths=[80 * mm, 80 * mm])
            table_params.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(Theme.LIGHT_BG)),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(Theme.LIGHT_TEXT)),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(Theme.LIGHT_BORDER)),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(table_params)
            elements.append(Spacer(1, 12))

            # Section BOM (Bill of Materials)
            elements.append(Paragraph("Bill of Materials (BOM)", style_section))

            entetes = ["ID", "Équipement", "Qté", "P.U. (€)", "Total (€)", "Stock"]
            data_bom = [entetes]
            for ligne in bom_resultat["lignes"]:
                statut_stock = "OK" if ligne["stock_suffisant"] else "RUPTURE"
                data_bom.append([
                    ligne["equipement_id"],
                    Paragraph(ligne["nom_equipement"], style_normal),
                    str(ligne["quantite"]),
                    f"{ligne['prix_unitaire']:.2f}",
                    f"{ligne['prix_total']:.2f}",
                    statut_stock,
                ])

            table_bom = Table(
                data_bom,
                colWidths=[15 * mm, 65 * mm, 15 * mm, 25 * mm, 28 * mm, 22 * mm],
                repeatRows=1,
            )

            style_table_bom = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Theme.PRIMARY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(Theme.LIGHT_BORDER)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (2, 0), (5, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor(Theme.LIGHT_BG)]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])

            # Mise en evidence des lignes en rupture de stock
            for i, ligne in enumerate(bom_resultat["lignes"], start=1):
                if not ligne["stock_suffisant"]:
                    style_table_bom.add(
                        "TEXTCOLOR", (5, i), (5, i),
                        colors.HexColor(Theme.DANGER)
                    )
                    style_table_bom.add(
                        "FONTNAME", (5, i), (5, i), "Helvetica-Bold"
                    )

            table_bom.setStyle(style_table_bom)
            elements.append(table_bom)
            elements.append(Spacer(1, 12))

            # Section totaux
            elements.append(Paragraph("Récapitulatif Financier", style_section))
            data_totaux = [
                ["Total HT", f"{bom_resultat['cout_total_ht']:.2f} €"],
                ["TVA (18%)", f"{bom_resultat['cout_tva']:.2f} €"],
                ["Total TTC", f"{bom_resultat['cout_total_ttc']:.2f} €"],
            ]
            table_totaux = Table(data_totaux, colWidths=[80 * mm, 60 * mm])
            table_totaux.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor(Theme.ACCENT_LIGHT)),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(Theme.LIGHT_BORDER)),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(table_totaux)
            elements.append(Spacer(1, 20))

            elements.append(Paragraph(
                "Document généré automatiquement par FiberSim — "
                "Outil de simulation et d'optimisation de réseau FO urbain.",
                ParagraphStyle("Footer", parent=styles["Normal"],
                               fontSize=7, textColor=colors.grey,
                               alignment=TA_CENTER)
            ))

            doc.build(elements)
            return True, chemin_sortie
        except Exception as e:
            return False, f"Erreur lors de l'export PDF : {e}"
