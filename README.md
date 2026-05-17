# SYNTHFLOW AI — Assistant Supply Chain

## Projet DU Data Analytics (Sorbonne)

Assistant intelligent pour la supply chain, combinant la recherche documentaire, des outils logistiques et une interface Streamlit.

### Objectif

Ce projet présente un assistant capable de :
- analyser des documents métiers (Incoterms, logistique, RSE),
- répondre à des questions sourcées avec un moteur RAG,
- exécuter des tâches via des agents LangChain,
- fournir des informations météo portuaire en temps réel.

### Fonctionnalités principales

- Recherche documentaire sur des documents internes indexés dans ChromaDB
- Orchestration d'agent avec LangChain
- Recherche web et données externes
- Interface Streamlit conviviale

### Structure du projet

- `main.py` : application Streamlit
- `engine_agents.py` : logique d'agent et outils
- `engine_rag.py` : indexation et recherche documentaire
- `data/` : documents métiers et ressources
- `vectorstore/` : base vectorielle locale
- `images/` : visuels de l'interface
- `requirements.txt` : dépendances Python

### Installation

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Crée un fichier `.env` dans le répertoire du projet.
2. Ajoute ta clé API Google AI Studio pour Gemini.
3. Vérifie que les documents à indexer sont bien présents dans `data/`.

### Lancement

```powershell
streamlit run main.py
```

### Remarques

- Ce projet utilise des contenus internes et des API externes.
- Ne partage pas de documents sensibles ou privés.
- Vérifie les droits avant de publier ou de rendre public des données tierces.

### Nom de dépôt recommandé

`github.com/ton-username/supplychain-ai-assistant`

### Licence

À adapter selon ton usage et les règles DU Sorbonne Data Analytics.
