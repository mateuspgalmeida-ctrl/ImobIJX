import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(page_title="ImobIJX | Inteligência Imobiliária", layout="wide", page_icon="🏢")

# 2. MOTOR DE ESTILO (CSS PREMIUM)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .kpi-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 5px solid #007a7c; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #007a7c; color: white; border-radius: 10px;
        border: none; height: 3em; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004d4d; color: white; border: none; }
    h1, h2, h3 { color: #004d4d; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL (ImobIJX)
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=180)
    else:
        st.title("🏢 ImobIJX")
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("MENU PRINCIPAL", [
        "📊 Dashboard Inicial", 
        "🏠 Gestão de Vendas",
        "👥 Equipe & Corretores", 
        "🧠 People Analytics (Match)", 
        "📄 Cadastro de Currículos"
    ])
    
    st.markdown("---")
    st.info("Copiloto Atlas: On-line 🤖")

# 4. LÓGICA DAS TELAS

# --- TELA: DASHBOARD INICIAL ---
if menu == "📊 Dashboard Inicial":
    st.title("Bem-vindo à ImobIJX")
    st.write("Visão geral da operação e performance da equipe.")
    st.markdown("---")
    
    # Linha 1: Métricas Principais (Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Vendas Totais", "R$ 2.8M", "+18%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Corretores Ativos", "37", "+2")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Taxa de Conversão", "5.4%", "+1.2%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Lead Score Médio", "78/100", "Bom")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Linha 2: Gráficos Principais
    col_graf_1, col_graf_2 = st.columns([2, 1])
    
    with col_graf_1:
        st.subheader("Performance de Vendas Mensal")
        # Gerando dados fictícios para o gráfico
        data_vendas = pd.DataFrame({
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'Vendas': [1.2, 1.5, 1.4, 1.9, 2.3, 2.8]
        }).set_index('Mês')
        st.area_chart(data_vendas, color="#007a7c")
        
    with col_graf_2:
        st.subheader("Composição da Equipe")
        # Gráfico de barras simples para representar a equipe
        equipe_data = pd.DataFrame({
            'Departamento': ['Vendas', 'Adm', 'Marketing', 'RH'],
            'Qtd': [25, 5, 4, 3]
        }).set_index('Departamento')
        st.bar_chart(equipe_data, color="#00b2b5")

    st.markdown("---")
    
    # Linha 3: Insight do Atlas
    st.subheader("🤖 Insights do Copiloto Atlas")
    st.success("""
        * **Foco em Fechamento:** Identificamos 5 leads com 90% de probabilidade de fechamento nesta semana.
        * **Equipe em Alta:** O match cultural da equipe subiu para 8.6 após o último treinamento.
        * **Alerta de Inventário:** A procura por apartamentos de 3 quartos no Centro aumentou 15%.
    """)

# --- TELA: GESTÃO DE VENDAS ---
elif menu == "🏠 Gestão de Vendas":
    st.title("Gestão de Vendas | ImobIJX")
    st.info("Módulo focado em pipeline e controle de inventário.")
    # (Código anterior de vendas aqui...)

# --- TELA: CADASTRO DE CURRÍCULOS ---
elif menu == "📄 Cadastro de Currículos":
    st.title("Portal de Talentos | ImobIJX")
    # (Código anterior de cadastro aqui...)

# --- TELA: MATCH COMPORTAMENTAL ---
elif menu == "🧠 People Analytics (Match)":
    st.title("Match Cultural | ImobIJX")
    # (Código anterior de analytics aqui...)

# RODAPÉ
st.markdown("<br><hr><center><b>ImobIJX</b> v1.3 | Desenvolvido pelo Atlas para Mateus</center>", unsafe_allow_html=True)
