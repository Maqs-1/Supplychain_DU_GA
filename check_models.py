import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la clé
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- DIAGNOSTIC DES MODÈLES DISPONIBLES ---")
try:
    for m in genai.list_models():
        # On filtre pour ne voir que les modèles capables de faire de l'embedding
        if 'embedContent' in m.supported_generation_methods:
            print(f"NOM : {m.name}")
            print(f"DESCRIPTION : {m.description}")
            print(f"LIMITES : {m.input_token_limit} tokens")
            print("-" * 30)
except Exception as e:
    print(f"Erreur lors de la connexion à l'API : {e}")