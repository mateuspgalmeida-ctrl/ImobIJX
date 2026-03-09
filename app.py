import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="ImobIJX | Gestão de Elite", layout="wide", page_icon="🏢")

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
        border: none; height: 3em; width: 100%; font-weight: bold;
    }
    h1, h2, h3 { color: #004d4d; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. BARRA LATERAL
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
    st.info("Atlas: Gestão de Talentos Ativa 🤖")

# 3. LÓGICA DAS TELAS

# --- TELA: DASHBOARD INICIAL ---
if menu == "📊 Dashboard Inicial":
    st.title("Dashboard Estratégico | ImobIJX")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VGV Total", "R$ 2.8M", "+18%")
    c2.metric("Corretores", "37", "Ativos")
    c3.metric("Conversão", "5.4%", "+1.2%")
    c4.metric("Novos Leads", "142", "Mês Atual")
    
    st.subheader("Tendência de Vendas")
    st.area_chart(np.random.randn(10, 1), color=["#007a7c"])

# --- TELA: EQUIPE & CORRETORES (CONTROLE TOTAL) ---
elif menu == "👥 Equipe & Corretores":
    st.title("Gestão de Pessoas | ImobIJX")
    
    tab_perfil, tab_cadastro, tab_prod = st.tabs([
        "🔍 Consultar Corretor", 
        "➕ Cadastrar Novo Membro", 
        "📈 Lançar Produtividade"
    ])
    
    # Lista simulada dos 37 corretores
    lista_corretores = [f"Corretor {i+1}" for i in range(37)]

    with tab_perfil:
        st.subheader("Ficha Individual de Performance")
        corretor_sel = st.selectbox("Selecione o profissional:", lista_corretores)
        
        col_inf1, col_inf2 = st.columns([1, 2])
        with col_inf1:
            st.markdown(f"""
            **Dados de: {corretor_sel}**
            - **Cargo:** Corretor Associado
            - **CRECI:** 12345-F
            - **Especialidade:** Alto Padrão
            - **Status:** Ativo
            """)
            st.button("Editar Cadastro")
        with col_inf2:
            st.write("Histórico de Vendas (Últimos 6 meses)")
            st.bar_chart(np.random.randint(1, 10, size=(6, 1)), color="#00b2b5")

    with tab_cadastro:
        st.subheader("Adicionar Novo Membro à ImobIJX")
        with st.form("form_novo_corretor"):
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                nome_n = st.text_input("Nome Completo")
                cpf_n = st.text_input("CPF")
                creci_n = st.text_input("CRECI")
            with c_c2:
                data_adm = st.date_input("Data de Início")
                especialidade = st.multiselect("Especialidades", ["Urbano", "Rural", "Luxo", "Minha Casa Minha Vida", "Lançamentos"])
                fone_n = st.text_input("WhatsApp")
            
            obs_n = st.text_area("Observações Internas (Perfil Comportamental)")
            
            btn_salvar_n = st.form_submit_button("Finalizar Cadastro")
            if btn_salvar_n:
                st.success(f"Corretor {nome_n} cadastrado com sucesso na base ImobIJX!")
                st.balloons()

    with tab_prod:
        st.subheader("Registro Mensal de Resultados")
        with st.form("form_prod_mensal"):
            c_p = st.selectbox("Selecionar Corretor", lista_corretores)
            mes_p = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"])
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                v_qtd = st.number_input("Vendas (Qtd)", min_value=0)
            with col_p2:
                c_qtd = st.number_input("Captações (Qtd)", min_value=0)
            with col_p3:
                vis_qtd = st.number_input("Visitas", min_value=0)
            
            vgv_l = st.number_input("VGV Total (R$)", min_value=0.0)
            
            btn_prod = st.form_submit_button("Salvar Resultados")
            if btn_prod:
                st.success(f"Resultados de {c_p} salvos. O Atlas atualizou o ranking de performance.")

# --- DEMAIS TELAS (RESERVADAS PARA PRÓXIMAS ATUALIZAÇÕES) ---
else:
    st.title(menu)
    st.info("Módulo operacional sob gestão do Atlas.")

# RODAPÉ
st.markdown("<br><hr><center><b>ImobIJX</b> v1.5 | Dashboard Administrativo de Alta Performance</center>", unsafe_allow_html=True)
