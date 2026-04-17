import streamlit as st
import ast
import base64
import html
import uuid
import json
import os

# ─── UTILITAIRE IMAGE ────────────────────────────────────────────────────────
def _img_to_data_url(path: str) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1]
    return f"data:image/{ext};base64,{data}"

# ─── TENTATIVE D'IMPORTATION (RÉSILIENCE) ────────────────────────────────────
AGENT_AVAILABLE = False
IMPORT_ERROR = None

try:
    from engine_agents import get_agent
    from langchain_core.messages import HumanMessage, AIMessage
    AGENT_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = str(e)

# ─── CONFIGURATION DE LA PAGE ────────────────────────────────────────────────
st.set_page_config(page_title="SYNTHFLOW AI - Supply Chain", page_icon="⚓", layout="centered")

# ─── MESSAGE D'ACCUEIL ───────────────────────────────────────────────────────
WELCOME_MSG = {
    "role": "assistant",
    "content": "Bonjour. Je suis **SYNTHFLOW**, votre assistant expert en Supply Chain.\n\nJe suis connecté à vos bases de données internes et au web. Vous pouvez me demander :\n- Une recherche sur les Incoterms ou vos contrats (PDF).\n- Le calcul d'une empreinte carbone maritime.\n- La météo en temps réel d'un port.\n- L'actualité du fret maritime.\n\nComment puis-je optimiser vos opérations aujourd'hui ?"
}

SESSIONS_FILE = "sessions.json"

def _new_session():
    sid = str(uuid.uuid4())
    st.session_state.sessions[sid] = {
        "title": "Nouvelle session",
        "messages": [WELCOME_MSG.copy()],
        "chat_history": []
    }
    return sid

def _save_sessions():
    data = {"active_session_id": st.session_state.active_session_id, "sessions": {}}
    for s_id, s_data in st.session_state.sessions.items():
        data["sessions"][s_id] = {
            "title": s_data["title"],
            "messages": s_data["messages"],
            "chat_history": [
                {"type": "human", "content": m.content} if isinstance(m, HumanMessage)
                else {"type": "ai", "content": m.content}
                for m in s_data["chat_history"]
            ]
        }
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return None, None
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sessions = {}
        for s_id, s_data in data.get("sessions", {}).items():
            chat_history = []
            if AGENT_AVAILABLE:
                for m in s_data.get("chat_history", []):
                    if m["type"] == "human":
                        chat_history.append(HumanMessage(content=m["content"]))
                    else:
                        chat_history.append(AIMessage(content=m["content"]))
            sessions[s_id] = {
                "title": s_data["title"],
                "messages": s_data["messages"],
                "chat_history": chat_history
            }
        return sessions, data.get("active_session_id")
    except Exception:
        return None, None

# ─── INITIALISATION DU SESSION STATE ─────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "sessions" not in st.session_state:
    loaded_sessions, loaded_active_id = _load_sessions()
    if loaded_sessions:
        st.session_state.sessions = loaded_sessions
        st.session_state.active_session_id = loaded_active_id
    else:
        st.session_state.sessions = {}
        first_sid = _new_session()
        st.session_state.active_session_id = first_sid

if "active_session_id" not in st.session_state:
    if st.session_state.sessions:
        st.session_state.active_session_id = next(iter(st.session_state.sessions))
    else:
        st.session_state.active_session_id = _new_session()

if "agent" not in st.session_state and AGENT_AVAILABLE:
    try:
        st.session_state.agent = get_agent()
    except:
        st.session_state.agent = None

# ─── SESSION ACTIVE ───────────────────────────────────────────────────────────
sid = st.session_state.active_session_id
session = st.session_state.sessions[sid]

# ─── RESSOURCES SELON LE THÈME ────────────────────────────────────────────────
is_dark = st.session_state.dark_mode

LOGO   = "images/app-name-dark.png"  if is_dark else "images/app-name-white.png"
AVATAR = _img_to_data_url("images/app-avatar-dark.png" if is_dark else "images/app-avatar-white.png")

# ─── VARIABLES CSS SELON LE THÈME ────────────────────────────────────────────
_bg           = "#0B0E14" if is_dark else "#FFFFFF"
_sidebar_bg   = "#0D1117" if is_dark else "#F8FAFC"
_text         = "#E2E8F0" if is_dark else "#1E293B"
_faq_hover    = "#60A5FA" if is_dark else "#2563EB"
_msg_border   = "rgba(255,255,255,0.07)" if is_dark else "rgba(0,0,0,0.08)"
_user_text    = "#E2E8F0" if is_dark else "#1E293B"
_sb_border    = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"
_input_bg     = "#1A1F2E" if is_dark else "#FFFFFF"
_input_border = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
_placeholder  = "#94A3B8"
_session_active_bg = "rgba(59,130,246,0.15)" if is_dark else "rgba(59,130,246,0.1)"
_session_active_border = "rgba(59,130,246,0.4)"

# ─── DESIGN CSS DYNAMIQUE ────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="block-container"],
    [data-testid="stVerticalBlock"] {{
        font-family: 'Inter', sans-serif !important;
        background-color: {_bg} !important;
        color: {_text} !important;
    }}

    /* Texte dans tous les composants Streamlit */
    p, span, div, h1, h2, h3, h4, label, li {{
        color: {_text} !important;
    }}

    footer {{visibility: hidden !important;}}
    header {{background-color: transparent !important;}}

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
        background-color: {_sidebar_bg} !important;
        border-right: 1px solid {_sb_border} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
        border-right: none !important;
    }}

    /* Bulles de chat — reset */
    .stChatMessage {{
        margin-bottom: 0.75rem !important;
        padding: 0 !important;
        border: none !important;
        background: none !important;
    }}

    /* Avatar assistant */
    [data-testid="chatAvatarIcon-assistant"] {{
        background-color: transparent !important;
    }}

    /* Contenu messages assistant */
    [data-testid="chatAvatarIcon-assistant"] ~ div {{
        padding: 1rem 1.25rem !important;
        border: 1px solid {_msg_border} !important;
        border-radius: 12px !important;
    }}

    /* Bulle utilisateur */
    .user-bubble {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 0.75rem;
    }}
    .user-bubble-content {{
        max-width: 72%;
        background-color: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: {_user_text};
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    /* Bloc fixe du bas (contient la zone de saisie) */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div {{
        background-color: {_bg} !important;
        border-top: none !important;
    }}

    /* Zone de saisie — wrapper extérieur = fond principal */
    [data-testid="stChatInput"] {{
        background-color: {_bg} !important;
    }}
    /* Bloc arrondi + champ de saisie */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea {{
        background-color: {_input_bg} !important;
        color: {_text} !important;
        border-color: {_input_border} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {_placeholder} !important;
        opacity: 1 !important;
    }}

    /* Bouton d'envoi — icône visible en mode sombre */
    [data-testid="stChatInput"] button svg {{
        fill: {_text} !important;
    }}

    .stChatInput {{
        padding-bottom: 2rem !important;
    }}

    /* Statut système */
    .status-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    .status-online {{ background-color: rgba(16,185,129,0.1); color: #10B981; border: 1px solid rgba(16,185,129,0.2); }}
    .status-offline {{ background-color: rgba(239,68,68,0.1); color: #EF4444; border: 1px solid rgba(239,68,68,0.2); }}

    /* Tous les boutons sidebar : base neutre */
    [data-testid="stSidebar"] button {{
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        text-align: left !important;
        cursor: pointer !important;
        width: 100% !important;
        border-radius: 0 !important;
        transition: color 0.15s ease !important;
    }}

    /* Nouvelle session — bouton primary */
    [data-testid="stSidebar"] button[kind="primary"] {{
        background-color: #3B82F6 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        min-height: 2.5rem !important;
        justify-content: center !important;
        transition: background-color 0.2s ease !important;
    }}
    [data-testid="stSidebar"] button[kind="primary"] * {{
        background-color: #3B82F6 !important;
        color: white !important;
    }}
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button[kind="primary"]:hover * {{
        background-color: #2563EB !important;
        color: white !important;
        text-decoration: none !important;
    }}

    /* Sessions passées */
    .session-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.6rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.85rem;
        color: {_text};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
        border: 1px solid transparent;
    }}
    .session-item.active {{
        background-color: {_session_active_bg};
        border-color: {_session_active_border};
    }}
    .session-item-icon {{
        flex-shrink: 0;
        opacity: 0.5;
        font-size: 0.8rem;
    }}

    /* Questions fréquentes — items de liste cliquables */
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] button[kind="secondary"] * {{
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: center !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: auto !important;
        font-size: 0.875rem !important;
        line-height: 1.8 !important;
        width: 100% !important;
        display: block !important;
        border-radius: 0 !important;
        cursor: pointer !important;
    }}
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    [data-testid="stSidebar"] button[kind="secondary"]:hover * {{
        color: {_faq_hover} !important;
        text-decoration: underline !important;
        background: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(LOGO)

    if AGENT_AVAILABLE:
        st.markdown('<div class="status-badge status-online">🟢 Système Opérationnel</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-offline">🔴 Hors Ligne</div>', unsafe_allow_html=True)
        st.error(f"Détail technique : \n`{IMPORT_ERROR}`")

    st.markdown("---")

    # ─── LISTE DES SESSIONS ───────────────────────────────────────────────────
    st.markdown("### Sessions")
    for s_id, s_data in reversed(list(st.session_state.sessions.items())):
        is_active = s_id == st.session_state.active_session_id
        label = s_data["title"]
        prefix = "▶ " if is_active else "   "
        if st.button(f"{prefix}{label}", key=f"session_{s_id}"):
            st.session_state.active_session_id = s_id
            st.rerun()

    if st.button("+ Nouvelle session", type="primary", use_container_width=True):
        new_sid = _new_session()
        st.session_state.active_session_id = new_sid
        _save_sessions()
        st.rerun()

    st.markdown("---")
    st.markdown("### Questions fréquentes")

    clicked_prompt = None

    if AGENT_AVAILABLE:
        if st.button("• Empreinte CO₂ (Shanghai - Le Havre)"):
            clicked_prompt = "Calcule l'empreinte CO2 pour 200 tonnes de Shanghai au Havre."
        if st.button("• Météo (Port de Rotterdam)"):
            clicked_prompt = "Quelle est la météo actuelle au port de Rotterdam ?"
        if st.button("• Responsabilités Incoterm FOB"):
            clicked_prompt = "Quelles sont les responsabilités sous l'Incoterm FOB d'après nos documents ?"
        if st.button("• Actus : Prix du fret maritime"):
            clicked_prompt = "Quelles sont les actualités récentes sur les prix du fret maritime ?"
        if st.button("• Politique RSE interne"):
            clicked_prompt = "Quelles sont les règles de notre politique RSE interne ?"

    st.markdown("---")
    st.markdown("### Capacités")
    st.markdown("-**RAG** : Analyse de documents internes")
    st.markdown("-**Web** : Recherche d'actualités")
    st.markdown("-**Outils** : Calculs & Empreinte CO₂")
    st.markdown("-**Météo** : Conditions portuaires")

    st.markdown("---")
    dark = st.toggle("Mode sombre", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

# ─── AFFICHAGE DE LA CONVERSATION ────────────────────────────────────────────
for message in session["messages"]:
    if message["role"] == "user":
        escaped = html.escape(message["content"])
        st.markdown(
            f'<div class="user-bubble"><div class="user-bubble-content">{escaped}</div></div>',
            unsafe_allow_html=True
        )
    else:
        with st.chat_message("assistant", avatar=AVATAR):
            st.markdown(message["content"])

# ─── BARRE DE SAISIE ET TRAITEMENT ───────────────────────────────────────────
input_placeholder = "Posez votre question opérationnelle..." if AGENT_AVAILABLE else "Connexion au moteur IA impossible."

user_input = st.chat_input(input_placeholder, disabled=not AGENT_AVAILABLE)

prompt = clicked_prompt or user_input

if prompt:
    # Titre auto depuis le premier message utilisateur
    if session["title"] == "Nouvelle session":
        session["title"] = prompt[:40] + ("…" if len(prompt) > 40 else "")

    session["messages"].append({"role": "user", "content": prompt})
    escaped = html.escape(prompt)
    st.markdown(
        f'<div class="user-bubble"><div class="user-bubble-content">{escaped}</div></div>',
        unsafe_allow_html=True
    )

    with st.chat_message("assistant", avatar=AVATAR):
        with st.status("Analyses en cours...", expanded=False) as status:
            try:
                response_obj = st.session_state.agent.invoke({
                    "input": prompt,
                    "chat_history": session["chat_history"]
                })

                raw_output = response_obj["output"]

                if isinstance(raw_output, list):
                    clean_text = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_output])
                    full_response = clean_text
                elif isinstance(raw_output, str) and raw_output.startswith("[{'type':"):
                    try:
                        parsed_list = ast.literal_eval(raw_output)
                        clean_text = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in parsed_list])
                        full_response = clean_text
                    except Exception:
                        full_response = raw_output
                else:
                    full_response = str(raw_output)

                status.update(label="Analyse terminée", state="complete")

            except Exception as e:
                full_response = f"⚠️ Échec du processus : {str(e)}"
                status.update(label="Erreur d'exécution", state="error")

        st.markdown(full_response)

    session["messages"].append({"role": "assistant", "content": full_response})
    session["chat_history"].extend([
        HumanMessage(content=prompt),
        AIMessage(content=full_response)
    ])

    _save_sessions()
    st.rerun()
