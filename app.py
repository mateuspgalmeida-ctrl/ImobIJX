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
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-top: 4px solid #007a7c; text-align: center;
    }
    .kpi-label { color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .kpi-val { color: #1e293b; font-size: 1.8rem; font-weight: 800; }
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
            st.success(f"Logado: {st.session_state.get('user_logado', 'Gestor')}")
            menu = st.radio("PAINEL ADMIN", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            st.write("---")
            if st.button("🚪 Sair do Sistema"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- TELAS PÚBLICAS ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #475569;'>Entender para atender.</p>", unsafe_allow_html=True)
                st.write("---")
                st.markdown("""
                ### Sobre a Plataforma
                O **ImobIJX** é o sistema central de inteligência da nossa imobiliária. 
                Aqui conectamos talentos, monitoramos resultados e transformamos dados em decisões.
                """)
        
        elif menu == "💼 Carreira":
            st.title("🎯 Oportunidades ImobIJX")
            st.info("Deixe seu currículo e faça parte do nosso time de elite.")
            with st.form("cv_publico"):
                nome = st.text_input("Nome Completo")
                zap = st.text_input("WhatsApp")
                link = st.text_input("Link do Currículo (Drive/LinkedIn)")
                exp = st.text_area("Fale sobre sua experiência")
                if st.form_submit_button("Submeter Candidatura"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([str(datetime.now().strftime("%d/%m/%Y %H:%M")), nome, zap, exp, link])
                        st.balloons()
                        st.success("Candidatura enviada!")

        elif menu == "🔐 Acesso Restrito":
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                st.title("🔐 Login")
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.button("Acessar Portal"):
                    if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")

    # --- TELAS ADMINISTRATIVAS ---
    else:
        gc = conecta_planilha()
        if not gc:
            st.error("Erro de conexão.")
            return

        df_corr = pd.DataFrame(gc.get_worksheet(0).get_all_records())
        
        # Limpeza e Conversão de Dados (Evita erros de cálculo)
        if not df_corr.empty:
            if 'Nota_Performance' in df_corr.columns:
                df_corr['Nota_Performance'] = pd.to_numeric(df_corr['Nota_Performance'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        if menu == "📊 Dashboard":
            st.title("📊 Indicadores de Performance")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Time de Vendas</p><p class="kpi-val">{len(df_corr)} Corretores</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="kpi-card"><p class="kpi-label">VGV Acumulado</p><p class="kpi-val">R$ 0,00</p></div>', unsafe_allow_html=True)
            with c3:
                total_cvs = len(gc.get_worksheet(2).get_all_records())
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Banco de Talentos</p><p class="kpi-val">{total_cvs} CVs</p></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("📈 Atividade Recente")
            st.bar_chart(np.random.randint(1, 10, 7), color="#007a7c")

        elif menu == "🧠 People Analytics":
            st.title("🧠 Inteligência de Dados e Talentos")
            if not df_corr.empty:
                c1, c2, c3 = st.columns(3)
                with c1:
                    nota_media = df_corr['Nota_Performance'].mean()
                    st.markdown(f'<div class="kpi-card"><p class="kpi-label">Média de Performance</p><p class="kpi-val">{nota_media:.1f}/10</p></div>', unsafe_allow_html=True)
                with c2:
                    perfil_dom = df_corr['Especialidade'].mode()[0] if 'Especialidade' in df_corr.columns else "N/A"
                    st.markdown(f'<div class="kpi-card"><p class="kpi-label">Perfil Dominante</p><p class="kpi-val">{perfil_dom}</p></div>', unsafe_allow_html=True)
                with c3:
                    skill_dom = df_corr['Habilidade_Principal'].mode()[0] if 'Habilidade_Principal' in df_corr.columns else "N/A"
                    st.markdown(f'<div class="kpi-card"><p class="kpi-label">Skill Principal</p><p class="kpi-val">{skill_dom}</p></div>', unsafe_allow_html=True)

                st.divider()
                col_rank, col_ficha = st.columns([1, 1.5])

                with col_rank:
                    st.subheader("🏆 Ranking de Elite")
                    ranking = df_corr.sort_values(by='Nota_Performance', ascending=False).head(5)
                    for i, row in enumerate(ranking.itertuples(), 1):
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
                        st.write(f"{medal} **{i}º {row.Nome}** - `{row.Nota_Performance:.1f}`")

                with col_ficha:
                    st.subheader("🔍 Raio-X do Talento")
                    nome_sel = st.selectbox("Selecione um profissional:", df_corr['Nome'].unique())
                    if nome_sel:
                        f = df_corr[df_corr['Nome'] == nome_sel].iloc[0]
                        with st.container(border=True):
                            # AJUSTE: Usando 'Especialidade' conforme sua planilha
                            esp_f = f.get('Especialidade', 'N/A')
                            hab_f = f.get('Habilidade_Principal', 'N/A')
                            st.markdown(f"**Especialidade:** `{esp_f}` | **Habilidade:** `{hab_f}`")
                            
                            try:
                                nota_f = float(f.get('Nota_Performance', 0))
                                st.progress(min(nota_f / 10, 1.0))
                                st.caption(f"Performance Atual: {nota_f}/10")
                            except:
                                st.caption("Nota indisponível")
            else:
                st.warning("Cadastre corretores para ativar o Analytics.")

        elif menu == "👥 Corretores":
            st.title("👥 Gestão da Equipe")
            t1, t2 = st.tabs(["Consultar Base", "Adicionar Corretor"])
            with t1:
                st.dataframe(df_corr, use_container_width=True, hide_index=True)
            with t2:
                with st.form("cad_admin"):
                    c1, c2 = st.columns(2)
                    n = c1.text_input("Nome")
                    cr = c2.text_input("CRECI")
                    # Ajustado para salvar na coluna 'Especialidade'
                    esp = st.selectbox("Especialidade", ["Urbano", "Rural", "Luxo", "Lançamentos"])
                    skill = st.selectbox("Habilidade Principal", ["Vendas", "Contratos", "Captação", "Networking"])
                    nota_ini = st.slider("Nota Inicial", 0.0, 10.0, 5.0)
                    if st.form_submit_button("Efetuar Cadastro"):
                        # Ordem baseada na sua planilha: Nome, CPF, CRECI, Data, Especialidade, WhatsApp, Habilidade, Nota
                        gc.get_worksheet(0).append_row([n, "", cr, str(datetime.now().date()), esp, "", skill, nota_ini])
                        st.success("Cadastrado com sucesso!")
                        st.rerun()

        elif menu == "💰 Vendas":
            st.title("💰 Controle Financeiro")
            with st.form("venda_fin"):
                corretores = df_corr['Nome'].tolist()
                sel_corr = st.selectbox("Corretor", corretores if corretores else ["Sem dados"])
                valor = st.number_input("Valor da Venda (R$)", min_value=0.0)
                if st.form_submit_button("Registrar Transação"):
                    st.success("Venda registrada para análise!")

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Currículos")
            df_cv = pd.DataFrame(gc.get_worksheet(2).get_all_records())
            st.dataframe(df_cv, use_container_width=True)

    st.markdown("<br><p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
