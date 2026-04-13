import streamlit as st
from engine_agents import get_agent
from langchain_core.messages import HumanMessage, AIMessage
import os

st.set_page_config(
    page_title="LOGIX — Supply Chain Intelligence",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --logix-bg:      #0A0D12;
    --logix-surface: #111620;
    --logix-card:    #161C28;
    --logix-border:  rgba(255,255,255,0.07);
    --logix-border2: rgba(255,255,255,0.12);
    --logix-accent:  #3B82F6;
    --logix-accent2: #06B6D4;
    --logix-green:   #10B981;
    --logix-text:    #F1F5F9;
    --logix-muted:   #64748B;
    --logix-sub:     #94A3B8;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--logix-bg) !important;
    color: var(--logix-text) !important;
}
.stApp { background: var(--logix-bg) !important; }

[data-testid="stSidebar"] {
    background: var(--logix-surface) !important;
    border-right: 1px solid var(--logix-border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 2rem 1.5rem; }

[data-testid="stMetric"] {
    background: var(--logix-card) !important;
    border: 1px solid var(--logix-border) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetric"]:hover { border-color: var(--logix-border2) !important; }
[data-testid="stMetricValue"] {
    color: var(--logix-text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--logix-muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

.stDataFrame, .stTable {
    border: 1px solid var(--logix-border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
thead th {
    background: var(--logix-card) !important;
    color: var(--logix-muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
tbody td {
    color: var(--logix-text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    border-bottom: 1px solid var(--logix-border) !important;
}

.stChatMessage { background: transparent !important; border: none !important; padding: 0.75rem 0 !important; }
[data-testid="stChatMessageUser"] { background: transparent !important; border: none !important; }
[data-testid="stChatMessageAssistant"] { background: transparent !important; border: none !important; }

[data-testid="stChatInput"] {
    background: var(--logix-card) !important;
    border: 1px solid var(--logix-border2) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--logix-accent) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--logix-text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--logix-muted) !important; }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--logix-card) !important;
    border: 1px solid var(--logix-border) !important;
    border-radius: 16px !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, var(--logix-accent), var(--logix-accent2)) !important;
    border-radius: 99px !important;
}
.stProgress > div { background: var(--logix-card) !important; border-radius: 99px !important; }

hr { border-color: var(--logix-border) !important; }
h1, h2, h3 { color: var(--logix-text) !important; font-family: 'Space Grotesk', sans-serif !important; }
.stCaption, small { color: var(--logix-muted) !important; font-size: 0.72rem !important; }
.stSpinner > div { border-top-color: var(--logix-accent) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--logix-border2); border-radius: 99px; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── HELPER : compte les chunks ChromaDB ─────────────────────────────────────
def get_doc_count() -> str:
    try:
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        if not os.path.exists("./vectorstore"):
            return "—"
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vs = Chroma(persist_directory="./vectorstore", embedding_function=embeddings)
        count = vs._collection.count()
        return str(count)
    except Exception:
        return "—"


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = get_agent()
if "doc_count" not in st.session_state:
    st.session_state.doc_count = get_doc_count()


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:0.25rem;'>
        <span style='font-family:Space Grotesk,sans-serif;font-size:1.7rem;font-weight:700;color:#F1F5F9;letter-spacing:-0.04em;'>LOGIX</span><span style='font-family:Space Grotesk,sans-serif;font-size:1.7rem;font-weight:300;color:#3B82F6;'>.</span>
    </div>
    <p style='font-size:0.65rem;letter-spacing:0.12em;color:#64748B;text-transform:uppercase;margin-bottom:0;font-weight:500;'>Supply Chain Intelligence</p>
    """, unsafe_allow_html=True)

    st.divider()

    st.metric(label="Navires actifs", value="42", delta="+3 vs hier")
    st.write("")
    st.metric(label="Retard moyen", value="1.8 h", delta="-0.4 h")
    st.write("")
    st.metric(label="Index carbone RSE", value="B+", delta="stable")

    st.divider()

    nb_docs = st.session_state.doc_count
    nb_messages = len([m for m in st.session_state.messages if m["role"] == "user"])

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:10px;'>
        <div style='width:7px;height:7px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981aa;'></div>
        <span style='font-size:0.7rem;color:#64748B;letter-spacing:0.06em;text-transform:uppercase;'>Système opérationnel</span>
    </div>
    <p style='font-size:0.68rem;color:#475569;font-family:JetBrains Mono,monospace;margin:3px 0;'>MODEL  · Gemini-2.5-Flash</p>
    <p style='font-size:0.68rem;color:#475569;font-family:JetBrains Mono,monospace;margin:3px 0;'>STORE  · ChromaDB</p>
    <p style='font-size:0.68rem;color:#475569;font-family:JetBrains Mono,monospace;margin:3px 0;'>CHUNKS · {nb_docs} indexés</p>
    <p style='font-size:0.68rem;color:#475569;font-family:JetBrains Mono,monospace;margin:3px 0;'>TOOLS  · 5 agents actifs</p>
    <p style='font-size:0.68rem;color:#475569;font-family:JetBrains Mono,monospace;margin:3px 0;'>MSG    · {nb_messages} échangés</p>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Réinitialiser la conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()


# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────
col_ops, col_chat = st.columns([1, 1.4], gap="large")


# ─── COL GAUCHE ───────────────────────────────────────────────────────────────
with col_ops:
    st.markdown("""
    <p style='font-size:0.68rem;letter-spacing:0.1em;color:#64748B;text-transform:uppercase;font-weight:600;margin-bottom:0.75rem;'>▸ Flux opérationnels</p>
    """, unsafe_allow_html=True)

    st.table({
        "UNITÉ":      ["CMA-01", "MSK-44", "HPL-09", "ONE-22"],
        "PARTENAIRE": ["CMA CGM", "MAERSK", "HAPAG", "ONE"],
        "STATUT":     ["🔵 TRANSIT", "🟢 QUAI", "🟡 LOAD", "🔴 MAINT"],
        "ETA":        ["14h30", "—", "09h00", "—"],
    })

    st.markdown("""
    <p style='font-size:0.68rem;letter-spacing:0.1em;color:#64748B;text-transform:uppercase;font-weight:600;margin-top:1.5rem;margin-bottom:0.5rem;'>▸ Objectif décarbonation RSE 2026</p>
    """, unsafe_allow_html=True)
    st.progress(82)
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Progression : **82%**")
    with c2:
        st.caption("Cible : 90%")

    st.divider()

    st.markdown("""
    <p style='font-size:0.68rem;letter-spacing:0.1em;color:#64748B;text-transform:uppercase;font-weight:600;margin-bottom:0.75rem;'>▸ Capacités de l'agent</p>
    <div style='display:flex;flex-wrap:wrap;gap:8px;'>
        <div style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#93C5FD;font-family:JetBrains Mono,monospace;'>📄 RAG Docs</div>
        <div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#6EE7B7;font-family:JetBrains Mono,monospace;'>🧮 Calculatrice</div>
        <div style='background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.25);border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#67E8F9;font-family:JetBrains Mono,monospace;'>⛅ Météo</div>
        <div style='background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.25);border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#C4B5FD;font-family:JetBrains Mono,monospace;'>🌿 CO₂ Maritime</div>
        <div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#FCD34D;font-family:JetBrains Mono,monospace;'>🌐 Recherche web</div>
    </div>
    """, unsafe_allow_html=True)


# ─── COL DROITE : CHAT ────────────────────────────────────────────────────────
with col_chat:
    st.markdown("""
    <p style='font-size:0.68rem;letter-spacing:0.1em;color:#64748B;text-transform:uppercase;font-weight:600;margin-bottom:0.75rem;'>▸ Interface stratégique</p>
    """, unsafe_allow_html=True)

    chat_placeholder = st.container(height=480, border=True)

    with chat_placeholder:
        if not st.session_state.messages:
            st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:300px;gap:12px;opacity:0.45;'>
                <div style='font-size:2.2rem;'>🚢</div>
                <p style='font-family:Space Grotesk,sans-serif;font-size:1rem;font-weight:500;color:#94A3B8;margin:0;'>LOGIX Intelligence Terminal</p>
                <p style='font-size:0.78rem;color:#64748B;text-align:center;max-width:300px;line-height:1.7;margin:0;'>
                    Posez une question sur vos documents internes, la météo d'un port, un calcul de coût ou l'empreinte carbone d'une expédition.
                </p>
            </div>
            """, unsafe_allow_html=True)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(
                    f"<div style='color:#F1F5F9;font-size:0.9rem;line-height:1.75;'>{message['content']}</div>",
                    unsafe_allow_html=True
                )

    # ─── SUGGESTIONS ─────────────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown("<p style='font-size:0.68rem;color:#475569;margin-top:0.6rem;margin-bottom:0.4rem;'>Suggestions rapides :</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⛅ Météo Rotterdam", use_container_width=True):
                st.session_state["_quick"] = "Quelle est la météo actuelle à Rotterdam ?"
                st.rerun()
        with c2:
            if st.button("🌿 CO₂ Shanghai → Le Havre", use_container_width=True):
                st.session_state["_quick"] = "Calcule l'empreinte carbone pour 300 tonnes de Shanghai à Le Havre"
                st.rerun()
        with c3:
            if st.button("📄 Incoterms FOB", use_container_width=True):
                st.session_state["_quick"] = "Explique-moi la règle Incoterms FOB et qui supporte les risques"
                st.rerun()

        c4, c5, c6 = st.columns(3)
        with c4:
            if st.button("🧮 Coût 3 conteneurs", use_container_width=True):
                st.session_state["_quick"] = "Calcule le coût total pour 3 conteneurs à 840€ avec 12% de surcharge carburant"
                st.rerun()
        with c5:
            if st.button("🌐 Prix du fret actuel", use_container_width=True):
                st.session_state["_quick"] = "Quels sont les prix du fret maritime actuels sur la route Asie-Europe ?"
                st.rerun()
        with c6:
            if st.button("📋 Politique RSE interne", use_container_width=True):
                st.session_state["_quick"] = "Quelle est notre politique RSE concernant les émissions carbone ?"
                st.rerun()

    # ─── INPUT ───────────────────────────────────────────────────────────────
    prompt = st.chat_input("Posez votre question logistique…")

    if "_quick" in st.session_state:
        prompt = st.session_state.pop("_quick")

    if prompt:
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(
                    f"<div style='color:#F1F5F9;font-size:0.9rem;line-height:1.75;'>{prompt}</div>",
                    unsafe_allow_html=True
                )
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_placeholder:
            with st.chat_message("assistant"):
                with st.spinner("Traitement en cours…"):
                    response_obj = st.session_state.agent.invoke({
                        "input": prompt,
                        "chat_history": st.session_state.chat_history
                    })
                    reponse = response_obj["output"]
                    st.markdown(
                        f"<div style='color:#F1F5F9;font-size:0.9rem;line-height:1.75;'>{reponse}</div>",
                        unsafe_allow_html=True
                    )

        st.session_state.messages.append({"role": "assistant", "content": reponse})
        st.session_state.chat_history.extend([
            HumanMessage(content=prompt),
            AIMessage(content=reponse)
        ])