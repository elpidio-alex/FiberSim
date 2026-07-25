# -*- coding: utf-8 -*-
"""
Génération du fichier Liste.xlsx : base de données des équipements FO.
"""
import pandas as pd

equipements = [
    {
        "ID": "EQ001",
        "Nom Équipement": "Antenne gNodeB 5G Massive MIMO",
        "Type": "Antenne",
        "Fabricant": "Huawei",
        "Prix Unitaire (€)": 8500.00,
        "Disponibilité (stock)": 12,
        "Spécifications Techniques": "64T64R, bande 3.5 GHz, portée 1.2 km, couverture 360°"
    },
    {
        "ID": "EQ002",
        "Nom Équipement": "Câble Fibre Optique Monomode G.652D",
        "Type": "Câble FO",
        "Fabricant": "Corning",
        "Prix Unitaire (€)": 1.85,
        "Disponibilité (stock)": 50000,
        "Spécifications Techniques": "12 brins, gaine extérieure, atténuation 0.35 dB/km, prix au mètre"
    },
    {
        "ID": "EQ003",
        "Nom Équipement": "Boîtier de Raccordement Optique (BPE)",
        "Type": "Boîtier",
        "Fabricant": "Nexans",
        "Prix Unitaire (€)": 145.00,
        "Disponibilité (stock)": 300,
        "Spécifications Techniques": "IP68, capacité 96 fibres, étanche, usage extérieur"
    },
    {
        "ID": "EQ004",
        "Nom Équipement": "OLT (Optical Line Terminal) GPON",
        "Type": "Équipement Central",
        "Fabricant": "ZTE",
        "Prix Unitaire (€)": 12000.00,
        "Disponibilité (stock)": 8,
        "Spécifications Techniques": "16 ports PON, jusqu'à 128 ONT/port, débit 2.5 Gbps down"
    },
    {
        "ID": "EQ005",
        "Nom Équipement": "ONT (Optical Network Terminal)",
        "Type": "Terminal Abonné",
        "Fabricant": "ZTE",
        "Prix Unitaire (€)": 55.00,
        "Disponibilité (stock)": 5000,
        "Spécifications Techniques": "1 port GPON, 4 ports Ethernet, WiFi intégré"
    },
    {
        "ID": "EQ006",
        "Nom Équipement": "Routeur Cœur de Réseau (Core Router)",
        "Type": "Routeur",
        "Fabricant": "Cisco",
        "Prix Unitaire (€)": 25000.00,
        "Disponibilité (stock)": 4,
        "Spécifications Techniques": "Débit 100 Gbps, redondance alimentation, châssis modulaire"
    },
    {
        "ID": "EQ007",
        "Nom Équipement": "Baie de Brassage Optique (ODF)",
        "Type": "Baie de Brassage",
        "Fabricant": "Huawei",
        "Prix Unitaire (€)": 780.00,
        "Disponibilité (stock)": 60,
        "Spécifications Techniques": "144 ports, montage rack 19 pouces, connecteurs SC/APC"
    },
    {
        "ID": "EQ008",
        "Nom Équipement": "Serveur Cœur de Réseau (Edge Server)",
        "Type": "Serveur",
        "Fabricant": "Dell",
        "Prix Unitaire (€)": 9800.00,
        "Disponibilité (stock)": 10,
        "Spécifications Techniques": "2x Xeon Silver, 128 Go RAM, virtualisation NFV"
    },
    {
        "ID": "EQ009",
        "Nom Équipement": "Fourreau PEHD pour pose souterraine",
        "Type": "Génie Civil",
        "Fabricant": "Plastiwell",
        "Prix Unitaire (€)": 3.20,
        "Disponibilité (stock)": 20000,
        "Spécifications Techniques": "Diamètre 40mm, tourets 500m, prix au mètre"
    },
    {
        "ID": "EQ010",
        "Nom Équipement": "Chambre de Tirage Béton L2T",
        "Type": "Génie Civil",
        "Fabricant": "Somaco",
        "Prix Unitaire (€)": 320.00,
        "Disponibilité (stock)": 150,
        "Spécifications Techniques": "Dimensions 63x40x40 cm, charge lourde, tampon fonte"
    },
    {
        "ID": "EQ011",
        "Nom Équipement": "Switch Agrégation Ethernet 48 ports",
        "Type": "Switch",
        "Fabricant": "Cisco",
        "Prix Unitaire (€)": 3200.00,
        "Disponibilité (stock)": 25,
        "Spécifications Techniques": "48 ports 1G/10G, SFP+ uplink, PoE+ 740W"
    },
    {
        "ID": "EQ012",
        "Nom Équipement": "Onduleur / Alimentation de Secours (UPS)",
        "Type": "Alimentation",
        "Fabricant": "APC",
        "Prix Unitaire (€)": 2100.00,
        "Disponibilité (stock)": 18,
        "Spécifications Techniques": "10 kVA, autonomie 45 min, rack 19 pouces"
    },
]

df = pd.DataFrame(equipements)
df.to_excel("/home/claude/fibersim/Liste.xlsx", index=False, sheet_name="Equipements")
print("Fichier généré avec", len(df), "équipements.")
