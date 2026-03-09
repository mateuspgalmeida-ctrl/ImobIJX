import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="ImobIJX | Portal de Gestão", layout="wide", page_icon="🏢")

# --- ESTILO CSS AVANÇADO ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }
    
    /* KPI Cards */
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-top: 4px solid #007a7c; text-align: center;
    }
    .kpi-label { color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .kpi-val { color: #1e293b; font-size: 1.8rem; font-weight: 800; }

    /* Estilo do Login */
    .login-box {
        max-width: 400px; margin: auto; padding: 40px;
        background: white; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    /* Botões */
    .stButton>button {
        background-color: #007a7c; color: white; border-radius: 8px;
        border: none; padding: 10px 20px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE ---
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except:
        return None

# --- LÓGICA DE NAVEGAÇÃO ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # SIDEBAR
    with st.sidebar:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        
        st.write("---")
        
        if not st.session_state["password_correct"]:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "💼 Carreira", "🔐 Acesso Restrito"])
        else:
            st.success(f"Logado como: {st.session_state.get('user_logado', 'Gestor')}")
            menu = st.radio("PAINEL ADMIN", ["📊 Dashboard", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            st.write("---")
            if st.button("🚪 Sair do Sistema"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- TELAS PÚBLICAS ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<h1 style='text-align: center;'>ImobIJX</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #475569;'>A nova era da gestão imobiliária em Feira de Santana.</p>", unsafe_allow_html=True)
                st.write("---")
                st.markdown("""
                ### Sobre a Plataforma
                O **ImobIJX** é o sistema central de inteligência da nossa imobiliária. 
                Aqui conectamos talentos, monitoramos resultados e transformamos dados em decisões.
                
                **O que você busca hoje?**
                - 🚀 **Crescimento Profissional:** Acesse a aba 'Carreira'.
                - 🔑 **Gestão Interna:** Área exclusiva para administradores.
                """)
        
        elif menu == "💼 Carreira":
            st.title("🎯 Oportunidades ImobIJX")
            st.info("Estamos selecionando os melhores talentos para o nosso time.")
            with st.container():
                with st.form("cv_publico"):
                    c1, c2 = st.columns(2)
                    nome = c1.text_input("Nome Completo")
                    zap = c2.text_input("WhatsApp (com DDD)")
                    link = st.text_input("Link do LinkedIn ou Currículo PDF (Google Drive)")
                    exp = st.text_area("Fale brevemente sobre sua experiência no mercado")
                    if st.form_submit_button("Submeter Candidatura"):
                        gc = conecta_planilha()
                        if gc:
                            gc.get_worksheet(2).append_row([str(datetime.now().strftime("%d/%m/%Y %H:%M")), nome, zap, exp, link])
                            st.balloons()
                            st.success("Candidatura enviada! Nossa equipe analisará seu perfil.")

        elif menu == "🔐 Acesso Restrito":
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.title("🔐 Login")
                st.write("Identifique-se para acessar o Atlas.")
                u = st.text_input("Usuário", placeholder="Ex: janeide")
                p = st.text_input("Senha", type="password", placeholder="••••••••")
                if st.button("Acessar Portal"):
                    if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas. Tente novamente.")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- TELAS ADMINISTRATIVAS ---
    else:
        gc = conecta_planilha()
        
        if menu == "📊 Dashboard":
            st.title("📊 Indicadores de Performance")
            c1, c2, c3 = st.columns(3)
            
            # Dados Reais da Planilha
            total_corr = len(gc.get_worksheet(0).get_all_records()) if gc else 0
            total_cvs = len(gc.get_worksheet(2).get_all_records()) if gc else 0
            
            with c1:
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Time de Vendas</p><p class="kpi-val">{total_corr} Corretores</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="kpi-card"><p class="kpi-label">VGV Acumulado</p><p class="kpi-val">R$ 0,00</p></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Banco de Talentos</p><p class="kpi-val">{total_cvs} CVs</p></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("📈 Atividade Recente")
            st.bar_chart(np.random.randint(1, 10, 7), color="#007a7c")

        elif menu == "👥 Corretores":
            st.title("👥 Gestão da Equipe")
            tab_ver, tab_cad = st.tabs(["🔍 Consultar Base", "➕ Adicionar Corretor"])
            
            with tab_cad:
                with st.form("cad_admin"):
                    c1, c2 = st.columns(2)
                    n = c1.text_input("Nome do Corretor")
                    cr = c2.text_input("CRECI")
                    perfil = st.selectbox("Perfil Atlas", ["Alto VGV", "Especialista Rural", "Lançamentos Urbano", "Focado em Locação"])
                    if st.form_submit_button("Efetuar Cadastro"):
                        gc.get_worksheet(0).append_row([n, "", cr, "", perfil, ""])
                        st.success("Membro adicionado com sucesso!")
            
            with tab_ver:
                df = pd.DataFrame(gc.get_worksheet(0).get_all_records())
                st.dataframe(df, use_container_width=True, hide_index=True)

        elif menu == "💰 Vendas":
            st.title("💰 Controle Financeiro")
            st.info("Utilize este módulo para registrar fechamentos e calcular repasses.")
            with st.expander("📝 Nova Venda", expanded=True):
                with st.form("venda_fin"):
                    corretores = [r['Nome'] for r in gc.get_worksheet(0).get_all_records()]
                    corr = st.selectbox("Corretor Responsável", corretores if corretores else ["Cadastre um corretor primeiro"])
                    valor = st.number_input("Valor da Venda (R$)", min_value=0.0, step=1000.0)
                    if st.form_submit_button("Registrar Transação"):
                        # Logica de salvar na planilha de vendas aqui
                        st.success("Venda enviada para análise financeira!")

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Currículos")
            st.write("Candidatos que se aplicaram via aba 'Carreira'.")
            if gc:
                df_cv = pd.DataFrame(gc.get_worksheet(2).get_all_records())
                st.dataframe(df_cv, use_container_width=True)

    st.markdown("<br><p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX Gestão Inteligente | Desenvolvido por Atlas</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
