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
        return None

def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

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
            menu = st.radio("PAINEL ADMIN", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()

    if st.session_state["password_correct"]:
        gc = conecta_planilha()
        if not gc: return

        df_corr = pd.DataFrame(gc.get_worksheet(0).get_all_records())
        df_vendas_raw = pd.DataFrame(gc.get_worksheet(1).get_all_records())
        
        hoje = datetime.now()
        meses_pt = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        
        # Inicialização de Variáveis de Filtro
        ano_sel = hoje.year
        mes_sel_nome = meses_pt[hoje.month]
        df_ano = pd.DataFrame()
        df_mes = pd.DataFrame()

        if not df_vendas_raw.empty:
            df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
            df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
            df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
            df_vendas_raw['Valor'] = pd.to_numeric(df_vendas_raw['Valor'].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
            df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

            # FILTROS NA SIDEBAR (Centralizados)
            st.sidebar.divider()
            st.sidebar.subheader("📅 Período de Análise")
            anos_disp = sorted(df_vendas_raw['Ano'].unique(), reverse=True)
            ano_sel = st.sidebar.selectbox("Ano", anos_disp if len(anos_disp) > 0 else [hoje.year])
            
            mes_sel_nome = st.sidebar.selectbox("Mês", list(meses_pt.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in meses_pt.items() if v == mes_sel_nome][0]

            df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel]
            df_mes = df_ano[df_ano['Mes_Num'] == mes_sel_num]

        # --- TELA DASHBOARD INTEGRADA ---
        if menu == "📊 Dashboard":
            st.title(f"📊 Painel de Resultados {ano_sel}")
            
            # 1. KPIs DO MÊS SELECIONADO
            st.subheader(f"📍 Resumo: {mes_sel_nome}")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV ({mes_sel_nome})</p><p class="kpi-val">R$ {df_mes["Valor"].sum():,.2f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Receita ({mes_sel_nome})</p><p class="kpi-val">R$ {df_mes["Comissão"].sum():,.2f}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Corretores Ativos</p><p class="kpi-val">{len(df_corr)}</p></div>', unsafe_allow_html=True)

            st.divider()

            # 2. GRÁFICOS LADO A LADO
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                st.subheader("🏆 VGV por Corretor (Anual)")
                if not df_ano.empty:
                    rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False)
                    fig_rank = px.bar(rank, x='Corretor', y='Valor', color='Corretor', text_auto='.2s', 
                                     color_discrete_sequence=px.colors.qualitative.Prism)
                    fig_rank.update_layout(showlegend=False)
                    st.plotly_chart(fig_rank, use_container_width=True)
                else:
                    st.info("Aguardando dados anuais.")

            with col_dir:
                st.subheader(f"📈 Resultados do Mês ({mes_sel_nome})")
                if not df_mes.empty:
                    # Gráfico Horizontal de Linhas (Performance Diária)
                    df_mes['Dia'] = df_mes['Data'].dt.day
                    evol_diaria = df_mes.groupby('Dia')['Valor'].sum().reset_index()
                    fig_linha = px.line(evol_diaria, x='Valor', y='Dia', orientation='h', markers=True,
                                       color_discrete_sequence=['#007a7c'])
                    st.plotly_chart(fig_linha, use_container_width=True)
                else:
                    st.info("Aguardando dados do mês.")

        # --- RESTANTE DOS MÓDULOS ---
        elif menu == "💰 Vendas":
            st.title("💰 Gestão de Vendas")
            st.subheader(f"Extrato Detalhado: {mes_sel_nome}/{ano_sel}")
            st.dataframe(df_mes[['Data', 'Corretor', 'Valor', 'Tipo_Operacao', 'Comissão']], use_container_width=True)
            
            with st.expander("➕ Nova Operação"):
                with st.form("nova_venda"):
                    c_v = st.selectbox("Corretor", df_corr['Nome'].tolist() if not df_corr.empty else ["Nenhum"])
                    t_v = st.selectbox("Operação", list(TAXAS_COMISSAO.keys()))
                    v_v = st.number_input("Valor", min_value=0.0)
                    d_v = st.date_input("Data", value=datetime.now())
                    if st.form_submit_button("Confirmar"):
                        gc.get_worksheet(1).append_row([str(d_v), c_v, v_v, t_v])
                        st.success("Operação Salva!")
                        st.rerun()

        elif menu == "🧠 People Analytics":
            st.title("🧠 Inteligência de Equipe")
            if not df_corr.empty:
                st.subheader("Distribuição de Especialistas")
                fig_pizza = px.pie(df_corr, names='Especialidade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_pizza, use_container_width=True)

        elif menu == "👥 Corretores":
            st.title("👥 Banco de Dados")
            st.dataframe(df_corr, use_container_width=True)

    # --- TELAS PÚBLICAS ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>ImobIJX</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>A nova era da gestão imobiliária em Feira de Santana.</p>", unsafe_allow_html=True)
        elif menu == "🔐 Acesso Restrito":
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"], st.session_state["user_logado"] = True, u
                    st.rerun()

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
