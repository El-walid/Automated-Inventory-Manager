import pandas as pd
import random

# Données réalistes pour Sidi Ghanem
categories = ["Ameublement", "Textile", "Décoration", "Luminaire"]
fournisseurs = ["Bois du Sud SARL", "Tissus Atlas", "Metal Pro Marrakech", "Import-Export 2026"]

data = {
    "Reference": [f"ART-{random.randint(1000,9999)}" for _ in range(50)],
    "Designation": [random.choice(["Chaise", "Table", "Tapis", "Lampe", "Fauteuil"]) + f" Modèle {i}" for i in range(1, 51)],
    "Categorie": [random.choice(categories) for _ in range(50)],
    "Fournisseur": [random.choice(fournisseurs) for _ in range(50)],
    "Stock_Actuel": [random.randint(0, 40) for _ in range(50)], 
    "Stock_Min_Securite": [10 for _ in range(50)],
    "Stock_Max_Cible": [50 for _ in range(50)],
    "Prix_Achat_Unitaire": [random.randint(50, 1500) for _ in range(50)],
    "Delai_Livraison_Jours": [random.choice([2, 5, 15, 30]) for _ in range(50)]
}

df = pd.DataFrame(data)
df.to_excel("Inventaire_Maroc" + str(random.randint(0, 100)) + ".xlsx", index=False)
print("✅ Fichier 'Inventaire_Maroc.xlsx' créé avec succès.")