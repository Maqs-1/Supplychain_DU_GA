from ds_python_interpreter import HTML
import os

# Contenu du README.md
readme_content = """# Assistant Intelligent Multi-Compétences (Agentique & RAG)
## Projet de Fin de Module - DU Data Analytics (Sorbonne Université Paris 1 Panthéon)

Ce projet consiste en la création d'un assistant intelligent capable de naviguer entre des documents internes (RAG) et l'exécution de tâches dynamiques via des agents (Tools). 

### 🏗️ Architecture du Système
L'application repose sur trois piliers technologiques :
1. **Moteur RAG (Retrieval-Augmented Generation)** : Indexation de documents PDF locaux dans une base vectorielle ChromaDB pour des réponses sourcées.
2. **Framework Agentique** : Utilisation de LangChain pour orchestrer un agent capable de décider quel outil utiliser en fonction de l'intention de l'utilisateur.
3. **Modèle de Langage (LLM)** : Google Gemini 2.5 Flash, sélectionné pour sa fenêtre de contexte étendue et sa rapidité de traitement.



### 🛠️ Fonctionnalités & Outils intégrés
L'agent dispose d'une "boîte à outils" composée de :
* **Recherche Documentaire** : Accès au corpus PDF interne (Incoterms, Logistique, RSE).
* **Calculatrice Logistique** : Exécution de calculs mathématiques précis pour les devis et volumes.
* **Météo Portuaire Temps Réel** : Connexion à l'API `wttr.in` pour évaluer les risques climatiques lors des chargements.
* **Recherche Web** : Capacité de recherche d'informations récentes pour compléter les connaissances internes.

### 🚀 Installation et Utilisation

#### 1. Prérequis
* Python 3.10+
* Une clé API Google AI Studio (Gemini)

#### 2. Installation des dépendances
```bash
pip install -r requirements.txt