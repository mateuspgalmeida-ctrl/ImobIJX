import streamlit as st
import pandas as pd

# Configuração da página e Cores da Logomarca
st.set_page_config(page_title="ImobIJX - Gestão de Talentos", layout="wide")

# CSS para injetar as cores da sua logo (Verdes e Tons Neutros)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #007a7c; color: white; border-radius: 8px; }
    .css-1d391kg { background-color: #ffffff; } /* Sidebar */
    h1, h2, h3 { color: #004d4d; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Barra Lateral) ---
with st.sidebar:
    st.image("logo.jpg", width=150) # Use o caminho da sua imagem aqui
    st.title("ImobIJX")
    st.markdown("---")
    menu = st.radio("Navegação", ["Painel de Controle", "Equipe Ativa", "Recrutamento", "Match Comportamental", "Performance (VRIO)"])

# --- CONTEÚDO PRINCIPAL ---
if menu == "Painel de Controle":
    st.title("KPIs de Gestão")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Crescimento da Equipe", "25", "+12%")
    with col2:
        st.metric("Taxa de Retenção", "73%", "5%")
    with col3:
        st.metric("Match Cultural Médio", "6.0", "Ideal: 8.5")

    st.markdown("---")
    st.subheader("Motor de Talento Atlas")
    
    with st.expander("Busca de Corretores", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            exp = st.slider("Nível de Experiência", 1, 5, 3)
        with col_b:
            perfil = st.multiselect("Perfil Desejado", ["Analítico", "Comunicador", "Executor", "Planejador"])
        
        if st.button("Confirmar Busca"):
            st.success("Filtrando os melhores perfis para a imobiliária...")

# Adicione as outras telas conforme a necessidade
