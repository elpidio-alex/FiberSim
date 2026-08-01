"""
Date : 01/08/2026
Auteur : Elpidio Alexis AMOUSSOU
Email : amoussouelpidioalexis@gmail.com

"""
# -*- coding: utf-8 -*-
"""
database.py
Connexion MySQL et gestion de l'historique des devis / projets FiberSim.
Necessite le package mysql-connector-python.
"""

import hashlib
import os
import re
from datetime import datetime

import mysql.connector
from mysql.connector import Error as MySQLError

from config import DBConfig


class Database:
    """Encapsule la connexion MySQL et les operations sur l'historique."""

    REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self):
        self.connection = None

    # --------------------------------------------------------
    # Connexion
    # --------------------------------------------------------
    def connect(self):
        """Etablit la connexion a MySQL et cree la base/tables si besoin."""
        try:
            self.connection = mysql.connector.connect(
                host=DBConfig.HOST,
                port=DBConfig.PORT,
                user=DBConfig.USER,
                password=DBConfig.PASSWORD,
            )
            cursor = self.connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DBConfig.DATABASE} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.close()
            self.connection.database = DBConfig.DATABASE
            self._create_tables()
            return True
        except MySQLError as e:
            print(f"[ERREUR MySQL] Connexion impossible : {e}")
            return False

    def is_connected(self):
        return self.connection is not None and self.connection.is_connected()

    def close(self):
        if self.is_connected():
            self.connection.close()

    # --------------------------------------------------------
    # Creation des tables
    # --------------------------------------------------------
    def _create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom_utilisateur VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mot_de_passe_hash VARCHAR(255) NOT NULL,
                sel VARCHAR(64) NOT NULL,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom_projet VARCHAR(150) NOT NULL,
                surface_km2 FLOAT NOT NULL,
                densite_habitants INT NOT NULL,
                nb_cellules_estime INT NOT NULL,
                cout_total_ht FLOAT NOT NULL,
                cout_total_ttc FLOAT NOT NULL,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                utilisateur_id INT,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devis_lignes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                projet_id INT NOT NULL,
                equipement_id VARCHAR(20),
                nom_equipement VARCHAR(200),
                quantite INT NOT NULL,
                prix_unitaire FLOAT NOT NULL,
                prix_total FLOAT NOT NULL,
                stock_suffisant TINYINT(1) DEFAULT 1,
                FOREIGN KEY (projet_id) REFERENCES projets(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        self.connection.commit()
        cursor.close()

    # --------------------------------------------------------
    # Authentification (PBKDF2)
    # --------------------------------------------------------
    @staticmethod
    def _hash_password(password, sel=None):
        if sel is None:
            sel = os.urandom(16).hex()
        hash_value = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(sel), 100_000
        ).hex()
        return hash_value, sel

    def creer_utilisateur(self, nom_utilisateur, email, password):
        if not self.REGEX_EMAIL.match(email):
            return False, "Adresse email invalide."

        try:
            hash_value, sel = self._hash_password(password)
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO utilisateurs "
                "(nom_utilisateur, email, mot_de_passe_hash, sel) "
                "VALUES (%s, %s, %s, %s)",
                (nom_utilisateur, email, hash_value, sel),
            )
            self.connection.commit()
            cursor.close()
            return True, "Utilisateur cree avec succes."
        except MySQLError as e:
            if e.errno == 1062:
                if "email" in str(e).lower():
                    return False, "Cette adresse email est deja utilisee."
                return False, "Ce nom d'utilisateur existe deja."
            return False, f"Erreur : {e}"

    def verifier_utilisateur(self, nom_utilisateur, password):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM utilisateurs WHERE nom_utilisateur = %s",
            (nom_utilisateur,),
        )
        user = cursor.fetchone()
        cursor.close()
        if not user:
            return False, None
        hash_value, _ = self._hash_password(password, user["sel"])
        if hash_value == user["mot_de_passe_hash"]:
            return True, user
        return False, None

    def compter_utilisateurs(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM utilisateurs")
        count = cursor.fetchone()[0]
        cursor.close()
        return count


    def modifier_utilisateur(self, user_id, nom_utilisateur=None, email=None,
                                nouveau_password=None):
            """
            Met a jour les champs fournis pour l'utilisateur donne.
            Seuls les champs non None sont modifies.
            """
            champs_a_mettre_a_jour = []
            valeurs = []

            if nom_utilisateur:
                champs_a_mettre_a_jour.append("nom_utilisateur = %s")
                valeurs.append(nom_utilisateur)

            if email:
                if not self.REGEX_EMAIL.match(email):
                    return False, "Adresse email invalide."
                champs_a_mettre_a_jour.append("email = %s")
                valeurs.append(email)

            if nouveau_password:
                hash_value, sel = self._hash_password(nouveau_password)
                champs_a_mettre_a_jour.append("mot_de_passe_hash = %s")
                champs_a_mettre_a_jour.append("sel = %s")
                valeurs.extend([hash_value, sel])

            if not champs_a_mettre_a_jour:
                return False, "Aucune modification fournie."

            valeurs.append(user_id)

            try:
                cursor = self.connection.cursor()
                requete = (
                    f"UPDATE utilisateurs SET {', '.join(champs_a_mettre_a_jour)} "
                    f"WHERE id = %s"
                )
                cursor.execute(requete, tuple(valeurs))
                self.connection.commit()
                cursor.close()
                return True, "Profil mis à jour avec succès."
            except MySQLError as e:
                if e.errno == 1062:
                    if "email" in str(e).lower():
                        return False, "Cette adresse email est déjà utilisée."
                    return False, "Ce nom d'utilisateur existe déjà."
                return False, f"Erreur : {e}"

    def obtenir_utilisateur_par_id(self, user_id):
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user


    # --------------------------------------------------------
    # Historique des projets / devis
    # --------------------------------------------------------
    def enregistrer_projet(self, nom_projet, surface_km2, densite_habitants,
                            nb_cellules_estime, cout_total_ht, cout_total_ttc,
                            lignes_bom, utilisateur_id=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """INSERT INTO projets
                   (nom_projet, surface_km2, densite_habitants,
                    nb_cellules_estime, cout_total_ht, cout_total_ttc,
                    utilisateur_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (nom_projet, surface_km2, densite_habitants,
                 nb_cellules_estime, cout_total_ht, cout_total_ttc,
                 utilisateur_id),
            )
            projet_id = cursor.lastrowid

            for ligne in lignes_bom:
                cursor.execute(
                    """INSERT INTO devis_lignes
                       (projet_id, equipement_id, nom_equipement, quantite,
                        prix_unitaire, prix_total, stock_suffisant)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (projet_id, ligne["equipement_id"], ligne["nom_equipement"],
                     ligne["quantite"], ligne["prix_unitaire"],
                     ligne["prix_total"], int(ligne["stock_suffisant"])),
                )

            self.connection.commit()
            cursor.close()
            return True, projet_id
        except MySQLError as e:
            return False, f"Erreur lors de l'enregistrement : {e}"

    def lister_projets(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projets ORDER BY date_creation DESC")
        projets = cursor.fetchall()
        cursor.close()
        return projets

    def obtenir_lignes_projet(self, projet_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM devis_lignes WHERE projet_id = %s", (projet_id,)
        )
        lignes = cursor.fetchall()
        cursor.close()
        return lignes

    def supprimer_projet(self, projet_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM projets WHERE id = %s", (projet_id,))
            self.connection.commit()
            cursor.close()
            return True
        except MySQLError as e:
            print(f"[ERREUR] Suppression impossible : {e}")
            return False