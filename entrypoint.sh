#!/bin/sh
set -e

# Construction de la base vectorielle si elle n'existe pas encore
if [ ! -d "./vectorstore" ] || [ -z "$(ls -A ./vectorstore 2>/dev/null)" ]; then
    echo "Vectorstore absent — construction en cours..."
    python engine_rag.py
else
    echo "Vectorstore déjà présent — démarrage direct."
fi

# Lancement de l'application
exec streamlit run main.py --server.port=8501 --server.address=0.0.0.0
