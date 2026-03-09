import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

# 2. MOTOR DE ESTILO (CSS PREMIUM CUSTOMIZADO)
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
    .stMetric label { color: #666; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL PERSONALIZADA (ImobIJX)
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=180)
    else:
        st.title("🏢 ImobIJX")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    menu = st.radio("MENU PRINCIPAL", [
        "📊 Painel de Performance", 
        "🏠 Gestão de Vendas",
        "👥 Equipe & Corretores", 
        "🧠 People Analytics (Match)", 
        "📈 Estratégia VRIO",
        "📄 Cadastro de Currículos"
    ])
    
    st.markdown("---")
    st.caption("Administrador: Mateus")
    st.info("Copiloto Atlas Operacional 🤖")

# 4. LÓGICA DAS TELAS

# --- TELA: PAINEL DE PERFORMANCE ---
if menu == "📊 Painel de Performance":
    st.title("Dashboard Estratégico | ImobIJX")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Vendas do Mês", "R$ 1.4M", "+15%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Novos Leads", "142", "+22%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Imóveis Captados", "28", "Meta: 35")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Taxa de Conversão", "4.2%", "+0.5%")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Tendência de Crescimento ImobIJX")
    chart_data = pd.DataFrame(np.random.rand(10, 2), columns=['Vendas Realizadas', 'Projeção Atlas'])
    st.line_chart(chart_data, color=["#007a7c", "#00b2b5"])

# --- TELA: GESTÃO DE VENDAS (NOVO!) ---
elif menu == "🏠 Gestão de Vendas":
    st.title("Gestão de Inventário e Vendas")
    st.write("Controle de imóveis e status de negociações.")
    
    tab1, tab2 = st.tabs(["Pipeline de Vendas", "Imóveis em Destaque"])
    
    with tab1:
        st.info("Pipeline integrado com o Atlas para predição de fechamento.")
        vendas = pd.DataFrame({
            'Imóvel': ['Apto Centro', 'Casa Condomínio', 'Terreno Industrial'],
            'Lead': ['Ricardo M.', 'Ana P.', 'Sérgio G.'],
            'Status': ['Proposta Enviada', 'Visita Agendada', 'Negociação Final'],
            'Probabilidade': ['85%', '60%', '95%']
        })
        st.table(vendas)
        
    with tab2:
        st.markdown("#### Filtro Inteligente")
        c1, c2 = st.columns(2)
        c1.selectbox("Tipo de Imóvel", ["Apartamento", "Casa", "Comercial", "Terreno"])
        c2.slider("Faixa de Preço (milhões)", 0.5, 5.0, 1.2)
        st.button("Buscar no Inventário ImobIJX")

# --- TELA: CADASTRO DE CURRÍCULOS ---
elif menu == "📄 Cadastro de Currículos":
    st.title("Portal de Talentos | ImobIJX")
    st.write("Venha fazer parte do time de alta performance.")
    
    with st.form("form_talent", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Profissional")
            tel = st.text_input("WhatsApp")
        with c2:
            vaga = st.selectbox("Área de Interesse", ["Vendas/Corretagem", "Administrativo", "Marketing", "RH/Analytics"])
            link = st.text_input("LinkedIn")
            cv = st.file_uploader("Currículo (PDF)", type=['pdf'])
            
        enviar = st.form_submit_button("Enviar para o Atlas")
        
        if enviar:
            if nome and cv:
                st.success(f"Cadastro de {nome} realizado! O Atlas iniciou o processamento do seu perfil.")
                st.balloons()
            else:
                st.warning("Preencha os campos obrigatórios e anexe seu currículo.")

# --- TELA: MATCH COMPORTAMENTAL ---
elif menu == "🧠 People Analytics (Match)":
    st.title("Inteligência Comportamental")
    st.write("Análise de fit cultural para a ImobIJX.")
    nome_analise = st.text_input("Nome do Colaborador")
    perfil = st.select_slider("Perfil Predominante", options=["Analista", "Planejador", "Comunicador", "Executor"])
    
    if st.button("Gerar Relatório Atlas"):
        st.success(f"Análise concluída para {nome_analise}! Perfil compatível com os valores da Janeide e da presidência.")

# RODAPÉ
st.markdown("<br><hr><center><b>ImobIJX</b> v1.2 | Sistema de Inteligência Imobiliária</center>", unsafe_allow_html=True)
