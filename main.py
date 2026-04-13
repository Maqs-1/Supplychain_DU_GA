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
st.set_page_config(page_title="LOGIX AI", page_icon="⚓", layout="centered")

# ─── DESIGN CSS (CHAT UI CUSTOM) ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fond et Polices */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0E1117 !important;
    }

    /* Masquer le menu Streamlit pour plus de propreté */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}

    /* Style des bulles de chat (Conteneur global) */
    .stChatMessage {
        padding: 1.5rem !important;
        border: none !important;
        background-color: transparent !important;
    }

    /* Ajustement spécifique pour l'utilisateur (Alignement à droite) */
    [data-testid="chatAvatarIcon-user"] { background-color: #3B82F6 !important; }
    
    /* Input fixe en bas */
    .stChatInput {
        padding-bottom: 2rem !important;
    }

    /* Indicateur de mode dégradé */
    .status-pill {
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(255,255,255,0.1);
        color: #94A3B8;
    }
</style>
""", unsafe_allow_html=True)

# ─── INITIALISATION DU SESSION STATE ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state and AGENT_AVAILABLE:
    try:
        st.session_state.agent = get_agent()
    except:
        st.session_state.agent = None

# ─── SIDEBAR (INFO DISCRÈTE) ─────────────────────────────────────────────────
with st.sidebar:
    st.title("⚓ LOGIX")
    st.markdown("Assistant logistique intelligent pour la Supply Chain.")
    
    if not AGENT_AVAILABLE:
        st.error(f"Erreur système détectée : \n`{IMPORT_ERROR}`")
        st.info("💡 Conseil : Installez la dépendance manquante avec pip.")
    
    st.divider()
    if st.button("Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# ─── ZONE DE RÉSULTATS (CHAT) ────────────────────────────────────────────────
st.markdown("<h3 style='text-align: center; color: white; margin-bottom: 2rem;'>Comment puis-je vous aider ?</h3>", unsafe_allow_html=True)

# Affichage des messages existants
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─── BARRE DE RECHERCHE (ZONE DE SAISIE) ─────────────────────────────────────
# On grise l'entrée si l'agent n'est pas prêt
input_placeholder = "Posez une question sur les Incoterms, le CO2 ou la météo..."
if not AGENT_AVAILABLE:
    input_placeholder = "Système hors ligne - Vérifiez les imports."

if prompt := st.chat_input(input_placeholder, disabled=not AGENT_AVAILABLE):
    
    # 1. Question de l'utilisateur (Affichée à droite par défaut dans Streamlit)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Réponse de l'assistant (Affichée à gauche)
    with st.chat_message("assistant"):
        with st.status("Logix en cours d'analyse...", expanded=False) as status:
            try:
                # Appel de l'agent
                response_obj = st.session_state.agent.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.chat_history
                })
                full_response = response_obj["output"]
                status.update(label="Réponse générée", state="complete")
            except Exception as e:
                full_response = f"⚠️ Une erreur est survenue : {str(e)}"
                status.update(label="Erreur technique", state="error")
        
        # Affichage du texte final
        st.markdown(full_response)

    # 3. Enregistrement historique
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.chat_history.extend([
        HumanMessage(content=prompt),
        AIMessage(content=full_response)
    ])