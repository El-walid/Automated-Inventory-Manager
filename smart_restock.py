import pandas as pd
from datetime import datetime
import time
from colorama import Fore, Style, init
from alerts import send_telegram_alert

init() # Initialisation des couleurs pour le terminal

print(Fore.CYAN + "🏭 DÉMARRAGE DU ROBOT D'APPROVISIONNEMENT (VERSION PRO)..." + Style.RESET_ALL)

# 1. CHARGEMENT
print("📂 Lecture du stock actuel...")
try:
    df = pd.read_excel("output/Inventaire_Maroc.xlsx")
except FileNotFoundError:
    print(Fore.RED + "❌ Erreur : Fichier 'output/Inventaire_Maroc.xlsx' introuvable." + Style.RESET_ALL)
    exit()

# 2. ANALYSE & CALCULS (PANDAS)
print("🧠 Analyse des besoins en cours...")

# On garde uniquement les produits où Stock Actuel < Stock Min
filtre_besoin = df['Stock_Actuel'] < df['Stock_Min_Securite']
df_commande = df[filtre_besoin].copy()

# Calcul 1 : Combien commander ? (Cible - Actuel)
df_commande['Qte_A_Commander'] = df_commande['Stock_Max_Cible'] - df_commande['Stock_Actuel']

# Calcul 2 : Budget nécessaire
df_commande['Budget_Total_DH'] = df_commande['Qte_A_Commander'] * df_commande['Prix_Achat_Unitaire']

# Calcul 3 : Niveau d'Urgence (Logique Python)
# Si le stock est à 0, c'est "CRITIQUE", sinon c'est "URGENT"
def definir_urgence(stock):
    if stock == 0:
        return "CRITIQUE (RUPTURE)"
    return "Priorité Haute"

# On applique la fonction sur toute la colonne (Apply = boucle rapide)
df_commande['Statut_Urgence'] = df_commande['Stock_Actuel'].apply(definir_urgence)

# Organisation des colonnes pour le rapport final
colonnes_finales = [
    'Reference', 'Designation', 'Fournisseur', 'Statut_Urgence', 
    'Stock_Actuel', 'Qte_A_Commander', 'Prix_Achat_Unitaire', 'Budget_Total_DH'
]
df_commande = df_commande[colonnes_finales]

# Tri : Les ruptures de stock (0) en premier
df_commande = df_commande.sort_values(by='Stock_Actuel', ascending=True)

# Totaux pour le résumé
total_articles = len(df_commande)
budget_global = df_commande['Budget_Total_DH'].sum()

print(Fore.YELLOW + f"⚠️  ALERTE : {total_articles} articles à commander.")
print(f"💰 Budget Estimé : {budget_global:,.2f} DH" + Style.RESET_ALL)

# --- ENVOI DES ALERTES TELEGRAM ---
if not df_commande.empty:
    print(Fore.MAGENTA + "📱 Envoi des alertes Telegram en cours..." + Style.RESET_ALL)
    for index, row in df_commande.iterrows():
        # On récupère les infos importantes
        nom_produit = row['Designation']
        stock = row['Stock_Actuel']
        urgence = row['Statut_Urgence']
        
        # On appelle la fonction importée depuis alerts.py
        # Le message sera personnalisé selon le statut (CRITIQUE ou Urgent)
        send_telegram_alert(nom_produit, stock)
    print(Fore.GREEN + "✅ Toutes les alertes ont été envoyées." + Style.RESET_ALL)
else:
    print(Fore.GREEN + "✅ Aucun besoin d'approvisionnement détecté. Pas d'alertes." + Style.RESET_ALL)

# 3. GÉNÉRATION EXCEL AVANCÉE (XLSXWRITER)
fichier_sortie = f"Bon_Commande_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
print(f"🎨 Création du fichier '{fichier_sortie}'...")

with pd.ExcelWriter(fichier_sortie, engine='xlsxwriter') as writer:
    # On écrit les données à partir de la ligne 4 (pour laisser de la place au titre)
    df_commande.to_excel(writer, sheet_name='Commande Fournisseurs', startrow=4, index=False)
    
    workbook = writer.book
    worksheet = writer.sheets['Commande Fournisseurs']
    
    # Titre Principal (Gros, Gras, Bleu)
    style_titre = workbook.add_format({
        'bold': True, 'font_size': 16, 'font_color': '#1F497D', 'align': 'left'
    })
    
    # Sous-titre (Date)
    style_date = workbook.add_format({
        'italic': True, 'font_color': '#555555'
    })
    
    # En-tête du tableau (Orange Sidi Ghanem, texte blanc)
    style_header = workbook.add_format({
        'bold': True, 'fg_color': '#ED7D31', 'font_color': 'white', 'border': 1, 'align': 'center'
    })
    
    # Colonne Argent (DH)
    style_argent = workbook.add_format({'num_format': '# ##0.00 "DH"', 'border': 1})
    
    # Style Alerte Rouge (Pour "CRITIQUE")
    style_rouge = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'bold': True, 'border': 1})
    
    # Style Normal (Bordures)
    style_bordure = workbook.add_format({'border': 1})

    # --- APPLICATION DU DESIGN ---
    
    # 1. Écrire le Titre en haut
    worksheet.write('A1', "RAPPORT AUTOMATIQUE D'APPROVISIONNEMENT", style_titre)
    worksheet.write('A2', f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", style_date)
    worksheet.write('A3', f"Budget Global Requis : {budget_global:,.2f} DH", style_titre)

    # 2. Formater les en-têtes de colonnes (Ligne 5, index 4)
    for col_num, value in enumerate(df_commande.columns.values):
        worksheet.write(4, col_num, value, style_header)

    # 3. Appliquer les largeurs de colonnes
    worksheet.set_column('A:A', 15) # Ref
    worksheet.set_column('B:B', 30) # Designation
    worksheet.set_column('C:C', 20) # Fournisseur
    worksheet.set_column('D:D', 20) # Statut
    worksheet.set_column('H:H', 20) # Budget

    # 4. Boucle pour formater les cellules ligne par ligne
    for row_num in range(len(df_commande)):
        # L'index Excel commence à 5 (car on a 4 lignes d'en-tête avant)
        excel_row = row_num + 5
        
        # --- A. GESTION DU STATUT (ROUGE OU NORMAL) ---
        statut = df_commande.iloc[row_num]['Statut_Urgence']
        if "CRITIQUE" in statut:
            worksheet.write(excel_row, 3, statut, style_rouge)
        else:
            worksheet.write(excel_row, 3, statut, style_bordure)
            
        # --- B. GESTION DES PRIX (FORMAT DH) ---
        
        # Colonne 6 : Prix Unitaire
        prix_unit = df_commande.iloc[row_num]['Prix_Achat_Unitaire']
        worksheet.write(excel_row, 6, prix_unit, style_argent)
        
        # Colonne 7 : Budget Total
        budget = df_commande.iloc[row_num]['Budget_Total_DH']
        worksheet.write(excel_row, 7, budget, style_argent)
        
        # (Optionnel) Ajoutons des bordures simples aux autres colonnes pour faire propre
        # Ref (0), Designation (1), Fournisseur (2), Stock (4), Qte (5)
        worksheet.write(excel_row, 0, df_commande.iloc[row_num]['Reference'], style_bordure)
        worksheet.write(excel_row, 1, df_commande.iloc[row_num]['Designation'], style_bordure)
        worksheet.write(excel_row, 2, df_commande.iloc[row_num]['Fournisseur'], style_bordure)
        worksheet.write(excel_row, 4, df_commande.iloc[row_num]['Stock_Actuel'], style_bordure)
        worksheet.write(excel_row, 5, df_commande.iloc[row_num]['Qte_A_Commander'], style_bordure)

print(Fore.GREEN + "✅ SUCCÈS ! Le fichier est prêt à être imprimé." + Style.RESET_ALL)

