import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
from datetime import datetime

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="ImobIJX | Portal de Gestão", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
TAXAS_COMISSAO = {
    "Venda (Imóvel Novo/Planta)": 0.05,
    "Venda (Usado/Terceiros)": 0.06,
    "Aluguel (1º Aluguel Integral)": 1.00,
    "Administração Mensal": 0.10,
    "Consultoria/Avaliação": 0.20
}

# --- ESTILO CSS ---
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
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE ---
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

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
            if st.button("🚪 Sair do Sistema"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- LÓGICA DE DADOS ADMIN ---
    if st.session_state["password_correct"]:
        gc = conecta_planilha()
        if not gc: return

        df_corr = pd.DataFrame(gc.get_worksheet(0).get_all_records())
        df_vendas_raw = pd.DataFrame(gc.get_worksheet(1).get_all_records())

        # Tratamento de Dados (Financeiro e Temporal)
        if not df_vendas_raw.empty:
            df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
            df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
            df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
            df_vendas_raw['Valor'] = pd.to_numeric(df_vendas_raw['Valor'].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
            df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

            # FILTROS SIDEBAR
            st.sidebar.divider()
            st.sidebar.subheader("📅 Filtros de Período")
            anos = sorted(df_vendas_raw['Ano'].dropna().unique().astype(int).tolist(), reverse=True)
            ano_sel = st.sidebar.selectbox("Ano de Análise", anos if anos else [datetime.now().year])
            
            meses_pt = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
            opcoes_mes = {v: k for k, v in meses_pt.items()}
            mes_sel_nome = st.sidebar.selectbox("Mês de Análise", list(opcoes_mes.keys()), index=datetime.now().month-1)
            mes_sel_num = opcoes_mes[mes_sel_nome]

            df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel]
            df_mes = df_ano[df_ano['Mes_Num'] == mes_sel_num]

        # --- TELAS ---
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard Estratégico {ano_sel}")
            
            # 1. KPIs DO MÊS SELECIONADO
            st.subheader(f"📍 Resultados de {mes_sel_nome}")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV MENSAL</p><p class="kpi-val">R$ {df_mes["Valor"].sum():,.2f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">RECEITA MENSAL</p><p class="kpi-val">R$ {df_mes["Comissão"].sum():,.2f}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">OPERAÇÕES</p><p class="kpi-val">{len(df_mes)}</p></div>', unsafe_allow_html=True)

            st.divider()

            # 2. EVOLUÇÃO TEMPORAL (LINHA)
            st.subheader(f"📈 Evolução de VGV em {ano_sel}")
            if not df_ano.empty:
                evol = df_ano.groupby('Mes_Num')['Valor'].sum().reset_index()
                evol['Mês'] = evol['Mes_Num'].map(meses_pt)
                fig_evol = px.line(evol, x='Mês', y='Valor', markers=True, color_discrete_sequence=['#007a7c'])
                st.plotly_chart(fig_evol, use_container_width=True)

            st.divider()

            # 3. RANKING COLORIDO POR CORRETOR (BARRA)
            st.subheader(f"🏆 Desempenho Anual por Corretor ({ano_sel})")
            if not df_ano.empty:
                rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False)
                fig_rank = px.bar(rank, x='Corretor', y='Valor', color='Corretor', 
                                 text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Bold)
                fig_rank.update_layout(showlegend=False)
                st.plotly_chart(fig_rank, use_container_width=True)
            else:
                st.info("Nenhuma operação registrada para este período.")

        elif menu == "🧠 People Analytics":
            st.title("🧠 Inteligência de Dados")
            if not df_corr.empty:
                # Ajuste de Nota
                df_corr['Nota_Performance'] = pd.to_numeric(df_corr['Nota_Performance'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                
                col_p1, col_p2 = st.columns([1, 1.5])
                with col_p1:
                    st.subheader("Mix de Especialidades")
                    fig_pizza = px.pie(df_corr, names='Especialidade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pizza, use_container_width=True)
                with col_p2:
                    st.subheader("Ficha de Performance")
                    sel = st.selectbox("Escolha um Corretor:", df_corr['Nome'].unique())
                    f = df_corr[df_corr['Nome'] == sel].iloc[0]
                    st.markdown(f"**Especialidade:** `{f.get('Especialidade', 'N/A')}`")
                    st.progress(float(f.get('Nota_Performance', 0))/10)
            else:
                st.warning("Cadastre corretores na aba '👥 Corretores'.")

        elif menu == "💰 Vendas":
            st.title("💰 Gestão Financeira")
            st.subheader(f"Extrato Detalhado: {mes_sel_nome}/{ano_sel}")
            st.dataframe(df_mes[['Data', 'Corretor', 'Valor', 'Tipo_Operacao', 'Comissão']], use_container_width=True)
            
            with st.expander("➕ Registrar Nova Operação"):
                with st.form("nova_venda"):
                    corr_v = st.selectbox("Corretor", df_corr['Nome'].tolist())
                    tipo_v = st.selectbox("Tipo de Operação", list(TAXAS_COMISSAO.keys()))
                    val_v = st.number_input("Valor Bruto (R$)", min_value=0.0)
                    data_v = st.date_input("Data da Venda", value=datetime.now())
                    if st.form_submit_button("Confirmar Registro"):
                        gc.get_worksheet(1).append_row([str(data_v), corr_v, val_v, tipo_v])
                        st.success("Venda registrada!")
                        st.rerun()

        elif menu == "👥 Corretores":
            st.title("👥 Gestão de Equipe")
            st.dataframe(df_corr, use_container_width=True)

    # --- TELAS PÚBLICAS ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>Portal de Gestão Inteligente - Feira de Santana.</p>", unsafe_allow_html=True)
        elif menu == "🔐 Acesso Restrito":
            st.title("🔐 Login Administrativo")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else:
                    st.error("Credenciais incorretas.")

    st.markdown("<br><p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
