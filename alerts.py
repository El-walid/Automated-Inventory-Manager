import requests
import os
from dotenv import load_dotenv

# --- LE CORRECTIF ---
# Force Python to find the .env file in the exact same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)
# --------------------

def send_telegram_alert(product_name, current_stock):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Ligne de débogage temporaire (à supprimer quand ça marchera !)
    if not TOKEN:
        print("❌ ERREUR CRITIQUE : Le TOKEN Telegram n'a pas été trouvé dans le fichier .env !")
        return
        
    message = f"⚠️ ALERTE STOCK : {product_name} est presque en rupture ({current_stock} unités restantes) ! 🛒 À commander d'urgence."
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Alert sent for {product_name}")
        else:
            print(f"❌ Failed to send alert for {product_name}: {response.text} / {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error: {e}")