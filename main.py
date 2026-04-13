import streamlit as st
import time

# ─── TENTATIVE D'IMPORTATION (RÉSILIENCE) ────────────────────────────────────
AGENT_AVAILABLE = False
IMPORT_ERROR = None

try:
    from engine_agents import get_agent
    from langchain_core.messages import HumanMessage, AIMessage
    AGENT_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = str(e)

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LOGIX AI", 
    page_icon="⚓", 
    layout="centered",
    initial_sidebar_state="expanded" # Force l'ouverture au démarrage 
)

# ─── DESIGN CSS (UI FIXE & CARDS) ────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0E1117 !important;
    }

    /* Désactiver le bouton de fermeture de la sidebar pour la rendre "fixe" */
    [data-testid="sidebar-close"] {
        display: none !important;
    }

    .stChatMessage {
        padding: 1.5rem !important;
        border: none !important;
        background-color: transparent !important;
    }

    [data-testid="chatAvatarIcon-user"] { background-color: #3B82F6 !important; }
    
    /* Style des cartes d'agents dans la sidebar */
    .agent-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.2s ease;
    }
    .agent-card:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3B82F6;
    }
    .agent-name {
        color: #F8FAFC;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-desc {
        color: #94A3B8;
        font-size: 0.75rem;
        margin-top: 4px;
        line-height: 1.3;
    }
</style>
""", unsafe_allow_html=True)

# ─── INITIALISATION DU SESSION STATE ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent_executor" not in st.session_state and AGENT_AVAILABLE:
    try:
        st.session_state.agent_executor = get_agent()
    except:
        st.session_state.agent_executor = None

# ─── SIDEBAR FIXE (LISTE DES AGENTS) ──────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:white; margin-bottom:0;'>⚓ LOGIX</h2>", unsafe_allow_html=True)
    st.caption("Terminal de Contrôle Logistique")
    
    st.divider()

    st.markdown("### 🦾 Capacités de l'IA")
    
    if AGENT_AVAILABLE and st.session_state.agent_executor:
        # On récupère dynamiquement les outils définis dans engine_agents.py
        for tool in st.session_state.agent_executor.tools:
            name = tool.name.replace("_", " ").title()
            # On tronque la description pour l'UI
            desc = tool.description.split('.')[0] 
            
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">🔹 {name}</div>
                <div class="agent-desc">{desc}.</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Moteur IA hors ligne")
        if IMPORT_ERROR:
            st.code(IMPORT_ERROR, language="bash")

    st.divider()
    if st.button("Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# ─── ZONE DE CHAT (CENTRALISÉE) ──────────────────────────────────────────────
st.markdown("<h4 style='text-align: center; color: #94A3B8; font-weight: 400;'>Comment puis-je vous aider aujourd'hui ?</h4>", unsafe_allow_html=True)

# Conteneur pour scroller
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ─── BARRE DE RECHERCHE ──────────────────────────────────────────────────────
input_placeholder = "Interroger Logix..."
if not AGENT_AVAILABLE:
    input_placeholder = "Erreur de chargement des modules."

if prompt := st.chat_input(input_placeholder, disabled=not AGENT_AVAILABLE):
    
    # Message utilisateur (à droite)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse assistant (à gauche)
    with st.chat_message("assistant"):
        with st.status("Logix réfléchit...", expanded=False) as status:
            try:
                # Appel effectif de l'agent
                response_obj = st.session_state.agent_executor.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.chat_history
                })
                full_response = response_obj["output"]
                status.update(label="Analyse terminée", state="complete")
            except Exception as e:
                full_response = f"⚠️ Erreur système : {str(e)}"
                status.update(label="Échec de l'analyse", state="error")
        
        st.markdown(full_response)

    # Sauvegarde
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    if AGENT_AVAILABLE:
        st.session_state.chat_history.extend([
            HumanMessage(content=prompt),
            AIMessage(content=full_response)
        ])