# Utilisation d'une image légère et stable
FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

# Arguments de construction pour la clé API (nécessaire pour l'étape de vectorisation)
ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY

# Installation des dépendances système nécessaires pour ChromaDB et la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir "numpy<2.0.0" && \
    pip install --no-cache-dir -r requirements.txt

# Copie de tout le code source et des documents (dossier /data)
COPY . .

# --- ÉTAPE CRUCIALE : Vectorisation des documents ---
# On génère la base de données vectorielle pendant la création de l'image
# pour que l'agent soit prêt dès le démarrage sur AWS.
RUN python engine_rag.py

# Exposition du port par défaut de Streamlit
EXPOSE 8501

# Variables d'environnement pour Streamlit
ENV PYTHONUNBUFFERED=1

# Commande de lancement de l'application Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]