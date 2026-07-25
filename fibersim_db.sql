-- =====================================================
-- FiberSim - Script de creation de la base de donnees
-- A executer dans MySQL Workbench (optionnel : l'appli
-- cree automatiquement ce schema au premier lancement)
-- =====================================================

CREATE DATABASE IF NOT EXISTS fibersim_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE fibersim_db;

-- ---------------------------------------------------
-- Table des utilisateurs (authentification PBKDF2 + email)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    sel VARCHAR(64) NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------
-- Table des projets (historique des devis - parametres
-- urbains + totaux financiers)
-- ---------------------------------------------------
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------
-- Table des lignes de devis (BOM detaille par projet)
-- ---------------------------------------------------
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------
-- Verification
-- ---------------------------------------------------
SHOW TABLES;
DESCRIBE utilisateurs;
DESCRIBE projets;
DESCRIBE devis_lignes;