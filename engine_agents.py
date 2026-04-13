import os
import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from engine_rag import query_documents

from engine_rag import query_documents

load_dotenv()

# ==========================================
# DISTANCES MARITIMES APPROXIMATIVES (km)
# ==========================================
DISTANCES_MARITIMES = {
    ("shanghai", "le havre"): 21000,
    ("shanghai", "rotterdam"): 20800,
    ("shanghai", "marseille"): 19500,
    ("shenzhen", "le havre"): 21200,
    ("hong kong", "le havre"): 21100,
    ("singapour", "le havre"): 15800,
    ("tokyo", "le havre"): 23000,
    ("busan", "le havre"): 22000,
    ("new york", "le havre"): 5850,
    ("new york", "rotterdam"): 5900,
    ("santos", "le havre"): 9800,
    ("valparaiso", "le havre"): 14000,
    ("dubai", "le havre"): 12500,
    ("djeddah", "le havre"): 8500,
    ("durban", "le havre"): 11000,
    ("lagos", "le havre"): 5200,
    ("hambourg", "le havre"): 750,
    ("rotterdam", "le havre"): 400,
    ("barcelone", "le havre"): 1500,
    ("genes", "le havre"): 2100,
    ("gênes", "le havre"): 2100,
}

FACTEUR_CO2 = 0.015  # kg CO2 par tonne-km (standard IMO)


# ==========================================
# 1. OUTILS DE L'AGENT
# ==========================================

@tool
def documents_internes(question: str) -> str:
    """Utile UNIQUEMENT pour chercher des informations dans les documents PDF de l'entreprise (Incoterms, RSE, contrats, politiques internes)."""
    return query_documents(question)


@tool
def calculatrice(expression: str) -> str:
    """Utile pour faire des calculs mathématiques. L'entrée doit être une expression mathématique (ex: 15 * 840 * 1.12)."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "Erreur : Impossible de calculer cette formule."


@tool
def meteo_portuaire(port: str) -> str:
    """Utile pour obtenir la météo RÉELLE et actuelle d'un port maritime ou d'une ville portuaire (ex: Rotterdam, Shanghai, Le Havre)."""
    try:
        url = f"https://wttr.in/{port}?format=Météo+à+%l+:+%C,+%t,+vent+%w"
        reponse = requests.get(url, timeout=5)
        reponse.encoding = "utf-8"
        if reponse.status_code == 200:
            return reponse.text
        else:
            return f"Impossible de récupérer la météo pour {port}."
    except Exception:
        return "Le service météo est actuellement indisponible."


@tool
def calculateur_co2(input: str) -> str:
    """
    Calcule l'empreinte carbone estimée d'un transport maritime.
    L'entrée doit contenir le tonnage, le port d'origine et le port de destination.
    Exemple : '200 tonnes de Shanghai à Le Havre' ou '500 t de Dubai à Rotterdam'.
    """
    try:
        import re

        tonnage_match = re.search(r"(\d+[\.,]?\d*)\s*(?:tonnes?|t\b)", input, re.IGNORECASE)
        if not tonnage_match:
            return "Erreur : précise le tonnage (ex: '200 tonnes de Shanghai à Le Havre')."
        tonnage = float(tonnage_match.group(1).replace(",", "."))

        trajet_match = re.search(r"de\s+(.+?)\s+[àa]\s+(.+?)(?:\s*$)", input, re.IGNORECASE)
        if not trajet_match:
            return "Erreur : précise l'origine et la destination (ex: 'de Shanghai à Le Havre')."
        origine = trajet_match.group(1).strip().lower()
        destination = trajet_match.group(2).strip().lower()

        distance = None
        for (orig, dest), km in DISTANCES_MARITIMES.items():
            if orig in origine and dest in destination:
                distance = km
                break
            if dest in origine and orig in destination:
                distance = km
                break

        if not distance:
            distance = 12000
            note = f"⚠️ Trajet '{origine} → {destination}' non répertorié. Distance estimée : {distance:,} km."
        else:
            note = f"📍 Distance maritime '{origine} → {destination}' : {distance:,} km."

        co2_kg = tonnage * distance * FACTEUR_CO2
        co2_tonnes = co2_kg / 1000
        arbres = int(co2_tonnes * 45)

        return f"""{note}

🚢 CALCUL D'EMPREINTE CARBONE MARITIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Tonnage transporté  : {tonnage:.0f} t
• Distance maritime   : {distance:,} km
• Facteur d'émission  : {FACTEUR_CO2} kg CO₂/t·km (standard IMO)

📊 RÉSULTAT
• Émissions totales   : {co2_kg:,.0f} kg CO₂
• Soit                : {co2_tonnes:,.2f} tonnes CO₂
• Équivalent          : {arbres} arbres à planter pour compenser (1 an)

💡 CONSEIL RSE
Slow steaming (-10% vitesse = -25% CO₂), optimisation du taux de remplissage,
ou compensation via programme de reforestation certifié."""

    except Exception as e:
        return f"Erreur lors du calcul CO2 : {str(e)}"


recherche_web = TavilySearchResults(
    max_results=3,
    description="Utile pour chercher des informations récentes sur internet : actualités, prix du fret, sanctions commerciales, réglementations douanières, cours des matières premières, etc."
)


# ==========================================
# 2. MOTEUR DE L'AGENT
# ==========================================

def get_agent():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    tools = [documents_internes, calculatrice, meteo_portuaire, calculateur_co2, recherche_web]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es LOGIX, un expert senior en Supply Chain et logistique internationale.
Tu assistes les équipes opérationnelles avec des réponses précises, professionnelles et actionnables.
Tu maintiens une conversation fluide et utilises l'historique pour comprendre le contexte.

TES 5 OUTILS :
- documents_internes : Incoterms, contrats, politiques RSE internes
- calculatrice : tout calcul numérique (coûts, surcharges, marges, volumes)
- meteo_portuaire : conditions météo d'un port ou d'une ville
- calculateur_co2 : empreinte carbone d'un transport maritime
- recherche_web : actualités, prix du fret, sanctions, réglementations récentes

RÈGLES CRITIQUES :
1. Après chaque outil, tu DOIS rédiger une réponse finale complète. Ne t'arrête jamais après un outil.
2. Analyse et explique le résultat dans le contexte de la question posée.
3. Ne devine jamais un calcul : utilise la calculatrice.
4. Ne devine jamais une règle Incoterms : cherche dans les documents internes.
5. CITATIONS : quand tu utilises documents_internes, cite la source (ex: 'D'après [nom du document]...').
6. Quand tu utilises recherche_web, mentionne les sources trouvées.
7. Pour toute question CO2 ou empreinte carbone maritime, utilise calculateur_co2.
8. Si on te demande s'il est prudent de charger ou d'appareiller, consulte la météo et donne un avis professionnel.

Réponds toujours en français, de manière professionnelle mais accessible."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )