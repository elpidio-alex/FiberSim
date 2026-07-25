# -*- coding: utf-8 -*-
"""
equipment_manager.py
Lecture, ecriture et gestion CRUD des equipements depuis un fichier Excel.
Aucun fichier n'est charge par defaut : l'utilisateur doit importer un
fichier Liste.xlsx au demarrage.
"""

import pandas as pd


class EquipmentManager:
    """Charge, modifie et persiste la liste des equipements (fichier Excel)."""

    COLONNES_ATTENDUES = [
        "ID", "Nom Équipement", "Type", "Fabricant",
        "Prix Unitaire (€)", "Disponibilité (stock)",
        "Spécifications Techniques"
    ]

    def __init__(self):
        self.chemin_fichier = None
        self.df = None

    # --------------------------------------------------------
    # Chargement
    # --------------------------------------------------------
    def charger(self, chemin_fichier):
        """Charge un fichier Excel choisi par l'utilisateur."""
        try:
            df_temp = pd.read_excel(chemin_fichier, sheet_name="Equipements")
            colonnes_manquantes = [
                c for c in self.COLONNES_ATTENDUES if c not in df_temp.columns
            ]
            if colonnes_manquantes:
                return False, (
                    f"Colonnes manquantes dans le fichier : {colonnes_manquantes}. "
                    f"Colonnes attendues : {self.COLONNES_ATTENDUES}"
                )

            self.df = df_temp
            self.chemin_fichier = chemin_fichier
            return True, f"Fichier importé avec succès ({len(self.df)} équipements)."
        except FileNotFoundError:
            return False, f"Fichier introuvable : {chemin_fichier}"
        except ValueError as e:
            return False, (
                f"Erreur de format : {e}. "
                f"Le fichier doit contenir une feuille nommée 'Equipements'."
            )
        except Exception as e:
            return False, f"Erreur lors du chargement : {e}"

    def est_charge(self):
        return self.df is not None

    # --------------------------------------------------------
    # Consultation
    # --------------------------------------------------------
    def obtenir_tous(self):
        if self.df is None:
            return []
        return self.df.to_dict(orient="records")

    def obtenir_par_id(self, equipement_id):
        if self.df is None:
            return None
        resultat = self.df[self.df["ID"] == equipement_id]
        if resultat.empty:
            return None
        return resultat.iloc[0].to_dict()

    def obtenir_par_type(self, type_equipement):
        if self.df is None:
            return []
        resultat = self.df[self.df["Type"] == type_equipement]
        return resultat.to_dict(orient="records")

    def types_disponibles(self):
        if self.df is None:
            return []
        return sorted(self.df["Type"].unique().tolist())

    def verifier_stock(self, equipement_id, quantite_demandee):
        equipement = self.obtenir_par_id(equipement_id)
        if equipement is None:
            return False, 0
        stock = equipement["Disponibilité (stock)"]
        return quantite_demandee <= stock, stock

    # --------------------------------------------------------
    # CRUD (ajout / modification / suppression)
    # --------------------------------------------------------
    def ajouter_equipement(self, donnees):
        """
        donnees : dict avec les cles ID, Nom Équipement, Type, Fabricant,
                  Prix Unitaire (€), Disponibilité (stock),
                  Spécifications Techniques
        """
        if self.df is None:
            return False, "Aucun fichier chargé. Importez d'abord un fichier Excel."

        if donnees.get("ID") in self.df["ID"].values:
            return False, f"Un équipement avec l'ID '{donnees.get('ID')}' existe déjà."

        colonnes_manquantes = [c for c in self.COLONNES_ATTENDUES if c not in donnees]
        if colonnes_manquantes:
            return False, f"Champs manquants : {colonnes_manquantes}"

        nouvelle_ligne = pd.DataFrame([donnees])[self.COLONNES_ATTENDUES]
        self.df = pd.concat([self.df, nouvelle_ligne], ignore_index=True)
        return True, "Équipement ajouté avec succès."

    def modifier_equipement(self, equipement_id, donnees):
        if self.df is None:
            return False, "Aucun fichier chargé."

        index = self.df.index[self.df["ID"] == equipement_id]
        if index.empty:
            return False, f"Équipement '{equipement_id}' introuvable."

        # Si l'ID est modifie, verifier qu'il n'entre pas en collision
        nouvel_id = donnees.get("ID", equipement_id)
        if nouvel_id != equipement_id and nouvel_id in self.df["ID"].values:
            return False, f"L'ID '{nouvel_id}' est déjà utilisé par un autre équipement."

        for colonne, valeur in donnees.items():
            if colonne in self.COLONNES_ATTENDUES:
                self.df.loc[index, colonne] = valeur

        return True, "Équipement modifié avec succès."

    def supprimer_equipement(self, equipement_id):
        if self.df is None:
            return False, "Aucun fichier chargé."

        if equipement_id not in self.df["ID"].values:
            return False, f"Équipement '{equipement_id}' introuvable."

        self.df = self.df[self.df["ID"] != equipement_id].reset_index(drop=True)
        return True, "Équipement supprimé avec succès."

    # --------------------------------------------------------
    # Sauvegarde (persistance sur disque)
    # --------------------------------------------------------
    def sauvegarder(self, chemin_fichier=None):
        """
        Ecrit le DataFrame courant dans le fichier Excel.
        Par defaut, ecrase le fichier source importe.
        """
        if self.df is None:
            return False, "Aucune donnée à sauvegarder."

        chemin_cible = chemin_fichier or self.chemin_fichier
        if not chemin_cible:
            return False, "Aucun chemin de fichier défini."

        try:
            self.df.to_excel(chemin_cible, index=False, sheet_name="Equipements")
            self.chemin_fichier = chemin_cible
            return True, f"Fichier sauvegardé : {chemin_cible}"
        except Exception as e:
            return False, f"Erreur lors de la sauvegarde : {e}"