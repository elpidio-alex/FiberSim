"""
Date : 01/08/2026
Auteur : Elpidio Alexis AMOUSSOU
Email : amoussouelpidioalexis@gmail.com

"""
# -*- coding: utf-8 -*-
"""
bom_calculator.py
Calcul du Bill of Materials (BOM) selon les parametres urbains du projet
(surface, densite d'habitants, nombre de cellules).

Regles de quantification (documentees dans le rapport technique) :
- Nombre de cellules = max(cellules demandees par l'utilisateur,
                           population totale / HABITANTS_PAR_CELLULE)
- Antennes gNodeB = 1 par cellule
- Cable FO (metres) = surface_km2 * CABLE_ML_PAR_KM2
- Fourreaux PEHD (metres) = cable_ml * RATIO_FOURREAU_CABLE
- Chambres de tirage = (cable_ml / 1000) * CHAMBRES_PAR_KM_CABLE
- BPE = cable_ml * BPE_PAR_ML_CABLE
- ONT = population_totale * TAUX_PENETRATION_FTTH
- OLT = ceil(nb_ONT / ONT_PAR_OLT)
- Switch agregation = 1 par OLT
- ODF (baie de brassage) = 1 par OLT
- Routeur coeur de reseau = 1 si nb_cellules < 20, sinon 2 (redondance)
- Serveur coeur de reseau = 1 si nb_cellules < 20, sinon 2 (redondance)
- Onduleur (UPS) = 1 par site actif (OLT + Routeur + Serveur confondus,
                    arrondi a l'entier superieur / 3 equipements par UPS)
"""

import math
from config import NetworkParams as NP


class BOMCalculator:
    """Calcule les quantites d'equipements necessaires pour un projet urbain."""

    # Association Type d'equipement -> fonction de calcul de quantite.
    # Cle = Type tel qu'il apparait dans Liste.xlsx.
    def __init__(self, equipment_manager):
        self.equipment_manager = equipment_manager

    def calculer_besoins(self, surface_km2, densite_habitants, nb_cellules_demande):
        """
        Calcule les besoins bruts (independamment du stock ou du choix
        utilisateur), sous forme de dict {Type: quantite}.
        """
        population_totale = int(surface_km2 * densite_habitants)

        nb_cellules_estime = max(
            nb_cellules_demande,
            math.ceil(population_totale / NP.HABITANTS_PAR_CELLULE)
        )

        cable_ml = surface_km2 * NP.CABLE_ML_PAR_KM2
        fourreau_ml = cable_ml * NP.RATIO_FOURREAU_CABLE
        nb_chambres = math.ceil((cable_ml / 1000) * NP.CHAMBRES_PAR_KM_CABLE)
        nb_bpe = math.ceil(cable_ml * NP.BPE_PAR_ML_CABLE)

        nb_ont = math.ceil(population_totale * NP.TAUX_PENETRATION_FTTH)
        nb_olt = max(1, math.ceil(nb_ont / NP.ONT_PAR_OLT))

        nb_switch = nb_olt
        nb_odf = nb_olt

        redondance = 2 if nb_cellules_estime >= 20 else 1
        nb_routeur = redondance
        nb_serveur = redondance

        nb_sites_actifs = nb_olt + nb_routeur + nb_serveur
        nb_ups = max(1, math.ceil(nb_sites_actifs / 3))

        return {
            "population_totale": population_totale,
            "nb_cellules_estime": nb_cellules_estime,
            "besoins_par_type": {
                "Antenne": nb_cellules_estime,
                "Câble FO": math.ceil(cable_ml),
                "Génie Civil - Fourreau": math.ceil(fourreau_ml),
                "Génie Civil - Chambre": nb_chambres,
                "Boîtier": nb_bpe,
                "Terminal Abonné": nb_ont,
                "Équipement Central": nb_olt,
                "Switch": nb_switch,
                "Baie de Brassage": nb_odf,
                "Routeur": nb_routeur,
                "Serveur": nb_serveur,
                "Alimentation": nb_ups,
            }
        }

    # Correspondance entre les libelles de besoins ci-dessus et le
    # champ "Type" reel present dans Liste.xlsx, ainsi que le champ
    # "Nom Équipement" attendu pour differencier cable/fourreau/chambre
    # qui partagent parfois le meme Type "Génie Civil".
    MAPPING_NOM = {
        "Génie Civil - Fourreau": "Fourreau",
        "Génie Civil - Chambre": "Chambre",
        "Câble FO": "Câble",
    }

    def generer_bom(self, surface_km2, densite_habitants, nb_cellules_demande,
                     equipements_selectionnes=None):
        """
        Genere le BOM complet : pour chaque equipement pertinent de
        Liste.xlsx, associe la quantite calculee, le prix unitaire,
        le prix total, et verifie le stock.

        equipements_selectionnes : liste d'ID d'equipements a inclure
            (si None, tous les equipements de Liste.xlsx sont consideres)

        Retourne un dict :
            {
                "population_totale": int,
                "nb_cellules_estime": int,
                "lignes": [ {equipement_id, nom_equipement, type,
                             quantite, prix_unitaire, prix_total,
                             stock_disponible, stock_suffisant}, ... ],
                "cout_total_ht": float
            }
        """
        besoins = self.calculer_besoins(
            surface_km2, densite_habitants, nb_cellules_demande
        )
        besoins_par_type = besoins["besoins_par_type"]

        tous_equipements = self.equipment_manager.obtenir_tous()
        lignes = []
        cout_total_ht = 0.0

        for eq in tous_equipements:
            eq_id = eq["ID"]
            if equipements_selectionnes is not None and eq_id not in equipements_selectionnes:
                continue

            type_eq = eq["Type"]
            nom_eq = eq["Nom Équipement"]

            # Determiner la cle de besoin correspondante
            quantite = 0
            if type_eq == "Génie Civil":
                if "Fourreau" in nom_eq:
                    quantite = besoins_par_type.get("Génie Civil - Fourreau", 0)
                elif "Chambre" in nom_eq:
                    quantite = besoins_par_type.get("Génie Civil - Chambre", 0)
            elif type_eq == "Câble FO":
                quantite = besoins_par_type.get("Câble FO", 0)
            else:
                quantite = besoins_par_type.get(type_eq, 0)

            if quantite <= 0:
                continue

            prix_unitaire = float(eq["Prix Unitaire (€)"])
            prix_total = round(quantite * prix_unitaire, 2)
            stock_disponible = int(eq["Disponibilité (stock)"])
            stock_suffisant = quantite <= stock_disponible

            lignes.append({
                "equipement_id": eq_id,
                "nom_equipement": nom_eq,
                "type": type_eq,
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "prix_total": prix_total,
                "stock_disponible": stock_disponible,
                "stock_suffisant": stock_suffisant,
            })

            cout_total_ht += prix_total

        cout_total_ht = round(cout_total_ht, 2)
        cout_tva = round(cout_total_ht * NP.TAUX_TVA, 2)
        cout_total_ttc = round(cout_total_ht + cout_tva, 2)

        return {
            "population_totale": besoins["population_totale"],
            "nb_cellules_estime": besoins["nb_cellules_estime"],
            "lignes": lignes,
            "cout_total_ht": cout_total_ht,
            "cout_tva": cout_tva,
            "cout_total_ttc": cout_total_ttc,
        }
