# Utilisation d'une image légère et stable
FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

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

# Rendre le script de démarrage exécutable
RUN chmod +x entrypoint.sh

# Exposition du port par défaut de Streamlit
EXPOSE 8501

# Variables d'environnement pour Streamlit
ENV PYTHONUNBUFFERED=1

# La vectorisation et le lancement se font à l'exécution (pas au build)
# GOOGLE_API_KEY doit être passée via --env ou les secrets du déploiement
ENTRYPOINT ["sh", "entrypoint.sh"]