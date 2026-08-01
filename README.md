<div align="center">

<img src="assets/logo.png" alt="FiberSim Logo" width="120"/>

# 📡 FiberSim

### Simulation et Optimisation de Réseaux Fibre Optique Urbains

*Outil de dimensionnement, chiffrage et export de devis pour projets de déploiement FTTH/5G*

[![Python](https://img.shields.io/badge/Python-3.11+-7C3AED?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-F59E0B?style=flat-square)](https://docs.python.org/3/library/tkinter.html)
[![MySQL](https://img.shields.io/badge/Database-MySQL-7C3AED?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-F59E0B?style=flat-square)](#-licence)
[![Status](https://img.shields.io/badge/Status-En%20développement-7C3AED?style=flat-square)](#)

</div>

---

## 📖 À propos

**FiberSim** est une application de bureau développée en Python permettant de **simuler, dimensionner et chiffrer** le déploiement d'un réseau de fibre optique (FTTH) couplé à une infrastructure 5G, à l'échelle d'une zone urbaine.

À partir de simples paramètres géographiques et démographiques (surface, densité de population, nombre de cellules souhaité), FiberSim calcule automatiquement les besoins matériels réels du projet — câblage, équipements actifs, boîtiers de raccordement, terminaux abonnés — en croisant ces besoins avec un inventaire d'équipements disponible, puis génère un **devis exportable** (CSV et PDF) prêt à être partagé avec un client ou une équipe technique.

Le projet a été conçu et développé par **Elpidio Alexis AMOUSSOU**, étudiant en Cybersécurité à l'iPNet Institute of Technology, dans le cadre d'un sprint personnel de 5 projets Python.

---

## ✨ Fonctionnalités principales

| Module | Description |
|---|---|
| 🔐 **Authentification** | Création de compte et connexion sécurisées (hachage **PBKDF2-HMAC** + sel unique par utilisateur) |
| 📦 **Gestion d'inventaire** | Import d'un fichier Excel (`Liste.xlsx`), CRUD complet des équipements (ajout, modification, suppression) |
| 🏙️ **Paramétrage de projet** | Saisie des données urbaines : surface (km²), densité de population, nombre de cellules souhaité |
| 🧮 **Calcul du BOM** | Génération automatique du *Bill of Materials* selon des règles de dimensionnement réseau documentées |
| 💰 **Chiffrage automatique** | Calcul des coûts HT/TTC (TVA 18%) avec vérification de disponibilité en stock |
| 📄 **Export de devis** | Export du devis généré aux formats **CSV** et **PDF** (mise en page professionnelle via `reportlab`) |
| 🕒 **Historique** | Sauvegarde et consultation des projets/devis précédents (base **MySQL**) |
| 👤 **Gestion de profil** | Modification du nom d'utilisateur, de l'email et du mot de passe |
| 🌗 **Thème clair / sombre** | Bascule globale et instantanée de l'interface, réglage Violet (`#7C3AED`) / Ambre (`#F59E0B`) |

---

## 🧠 Logique métier — Algorithme de dimensionnement

FiberSim applique des règles de quantification réseau pour convertir des paramètres urbains bruts en besoins matériels concrets :

Population totale = surface_km² × densité_habitants
Nombre de cellules = max(cellules demandées, population / 2500)
Câble FO (mètres) = surface_km² × 1200
Fourreaux PEHD (mètres) = câble_ml × 1.0
Chambres de tirage = (câble_ml / 1000) × 4
Boîtiers BPE = câble_ml × (1 / 500)
Terminaux ONT = population_totale × 35% (taux de pénétration FTTH)
OLT = ⌈ONT / (128 × 16)⌉
Switch d'agrégation = 1 par OLT
ODF (baie de brassage) = 1 par OLT
Routeur cœur de réseau = 1 (ou 2 en redondance si ≥ 20 cellules)
Serveur cœur de réseau = 1 (ou 2 en redondance si ≥ 20 cellules)
Onduleur (UPS) = 1 pour 3 équipements actifs


Chaque ligne du devis croise ensuite ces quantités théoriques avec le stock réellement disponible dans l'inventaire Excel, afin de signaler toute rupture avant validation du projet.

---

## 🏗️ Architecture du projet

```

fibersim/
│
├── main.py # Point d'entrée — fenêtre principale, navigation, thème global
├── config.py # Thème visuel, configuration MySQL, chemins, constantes métier
├── database.py # Connexion MySQL, authentification PBKDF2, historique des projets
├── equipment_manager.py # Lecture / CRUD de l'inventaire (fichier Excel)
├── bom_calculator.py # Moteur de calcul du Bill of Materials
├── export_manager.py # Génération des exports CSV et PDF (reportlab)
├── generate_liste.py # Script de génération du fichier Liste.xlsx (données de démo)
├── fibersim_db.sql # Script SQL de création manuelle du schéma MySQL
├── Liste.xlsx # Base de données des équipements (feuille "Equipements")
├── requirements.txt # Dépendances Python
├── .env.example # Modèle de configuration des variables d'environnement
│
├── ui/ # Interface graphique (Tkinter)
│ ├── login_frame.py # Écran de connexion / création de compte
│ ├── sidebar.py # Barre latérale de navigation (pliable)
│ ├── inventory_frame.py # Écran de gestion de l'inventaire
│ ├── project_params_frame.py # Écran de saisie des paramètres du projet
│ ├── bom_frame.py # Écran de génération et export du devis
│ ├── history_frame.py # Écran d'historique des projets
│ └── profile_frame.py # Écran de gestion du profil utilisateur
│
└── assets/
├── logo.png # Logo de l'application
└── logo.ico # Icône de la fenêtre

```


---

## 🛠️ Stack technique

- **Langage** : Python 3.11+
- **Interface graphique** : Tkinter
- **Traitement de données** : Pandas, OpenPyXL
- **Base de données** : MySQL (via `mysql-connector-python`)
- **Génération de PDF** : ReportLab
- **Gestion des images** : Pillow
- **Sécurité** : Hachage de mots de passe PBKDF2-HMAC avec sel unique
- **Configuration** : Variables d'environnement via `python-dotenv`

---

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- Un serveur MySQL local ou distant (optionnel — l'application reste utilisable en mode dégradé sans base de données)

### Étapes

**1. Cloner le dépôt**

```bash
git clone https://github.com/elpidio-alex/fibersim.git
cd fibersim
```

**2. Créer et activer un environnement virtuel**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**4. Configurer les variables d'environnement**

```bash
cp .env.example .env
```

Puis éditer le fichier `.env` avec vos identifiants MySQL :

```env
FIBERSIM_DB_HOST=localhost
FIBERSIM_DB_PORT=3306
FIBERSIM_DB_USER=root
FIBERSIM_DB_PASSWORD=votre_mot_de_passe
FIBERSIM_DB_NAME=fibersim_db
```

> ⚠️ Le fichier `.env` est ignoré par Git (`.gitignore`) et ne doit **jamais** être commité.

**5. (Optionnel) Créer manuellement le schéma MySQL**

La base et les tables sont créées automatiquement au premier lancement. Il est toutefois possible d'exécuter le script SQL manuellement :

```bash
mysql -u root -p < fibersim_db.sql
```

**6. Lancer l'application**

```bash
python main.py
```

Un fichier `Liste.xlsx` d'exemple est fourni. Il peut être régénéré à tout moment via :

```bash
python generate_liste.py
```

---

## 📋 Utilisation

1. **Connexion** : créez un compte ou connectez-vous à l'écran d'accueil.
2. **Inventaire** : importez votre fichier `Liste.xlsx` (feuille `Equipements`), consultez et modifiez le stock disponible.
3. **Paramètres du projet** : renseignez la surface (km²), la densité d'habitants et le nombre de cellules souhaité.
4. **Génération du devis** : FiberSim calcule automatiquement le BOM, vérifie la disponibilité des stocks et affiche le coût total HT/TTC.
5. **Export** : exportez le devis final au format CSV ou PDF.
6. **Historique** : retrouvez tous vos projets précédemment enregistrés (nécessite une connexion MySQL active).

---

## 📁 Format attendu du fichier `Liste.xlsx`

Le fichier d'inventaire doit contenir une feuille nommée **`Equipements`** avec les colonnes suivantes :

```

| Colonne | Type | Description |
|---|---|---|
| `ID` | Texte | Identifiant unique de l'équipement |
| `Nom Équipement` | Texte | Désignation commerciale |
| `Type` | Texte | Catégorie (Antenne, Câble FO, OLT, ONT, etc.) |
| `Fabricant` | Texte | Nom du fabricant |
| `Prix Unitaire (€)` | Numérique | Prix unitaire hors taxes |
| `Disponibilité (stock)` | Numérique | Quantité disponible en stock |
| `Spécifications Techniques` | Texte | Détails techniques de l'équipement |

```

---

## 🔒 Sécurité

- Mots de passe jamais stockés en clair : hachage **PBKDF2-HMAC** avec sel aléatoire propre à chaque utilisateur.
- Identifiants de base de données externalisés via variables d'environnement (`python-dotenv`), jamais codés en dur.
- Le fichier `.env` réel est exclu du contrôle de version via `.gitignore`.

---

## 🗺️ Roadmap

- [ ] Visualisation cartographique de la couverture réseau
- [ ] Export du devis au format Excel natif
- [ ] Gestion multi-projets simultanés avec comparaison de scénarios
- [ ] Authentification à deux facteurs (2FA)
- [ ] Version packagée (exécutable `.exe` autonome)

---

## 👤 Auteur

**Elpidio Alexis AMOUSSOU**
Étudiant en Cybersécurité — iPNet Institute of Technology (Lomé, Togo)
Formateur cybersécurité chez TeCoX

- GitHub : [@elpidio-alex](https://github.com/elpidio-alex)
- Email : amoussouelpidioalexis@gmail.com

---

## 📜 Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

---

<div align="center">

*Développé avec 💜 et ☕ dans le cadre d'un sprint de 5 projets Python en cybersécurité — Projet 5/5.*

**#Python #Cybersécurité #IPNET #L2Cybersécurité**

</div>