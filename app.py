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
    except Exception:
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
            # MENU COMPLETO RESTAURADO
            menu = st.radio("PAINEL ADMIN", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
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
        
        # Estrutura padrão para evitar erros
        colunas_vendas = ['Data', 'Corretor', 'Valor', 'Tipo_Operacao', 'Comissão', 'Ano', 'Mes_Num']
        df_ano = pd.DataFrame(columns=colunas_vendas)
        df_mes = pd.DataFrame(columns=colunas_vendas)
        ano_sel, mes_sel_nome = hoje.year, meses_pt[hoje.month]

        if not df_vendas_raw.empty:
            df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
            df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
            df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
            df_vendas_raw['Valor'] = pd.to_numeric(df_vendas_raw['Valor'].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
            df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

            st.sidebar.divider()
            st.sidebar.subheader("📅 Período de Análise")
            anos_disp = sorted([int(a) for a in df_vendas_raw['Ano'].dropna().unique()], reverse=True)
            ano_sel = st.sidebar.selectbox("Ano", anos_disp if anos_disp else [hoje.year])
            mes_sel_nome = st.sidebar.selectbox("Mês", list(meses_pt.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in meses_pt.items() if v == mes_sel_nome][0]
            df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel]
            df_mes = df_ano[df_ano['Mes_Num'] == mes_sel_num]

        # --- TELAS ---
        if menu == "📊 Dashboard":
            st.title(f"📊 Painel de Resultados {ano_sel}")
            vgv_m = df_mes["Valor"].sum() if "Valor" in df_mes.columns else 0
            rec_m = df_mes["Comissão"].sum() if "Comissão" in df_mes.columns else 0
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV ({mes_sel_nome})</p><p class="kpi-val">R$ {vgv_m:,.2f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Receita ({mes_sel_nome})</p><p class="kpi-val">R$ {rec_m:,.2f}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Time</p><p class="kpi-val">{len(df_corr)}</p></div>', unsafe_allow_html=True)

            st.divider()
            col_esq, col_dir = st.columns(2)
            with col_esq:
                st.subheader("🏆 VGV por Corretor (Anual)")
                if not df_ano.empty:
                    rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False)
                    fig_rank = px.bar(rank, x='Corretor', y='Valor', color='Corretor', text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Prism)
                    fig_rank.update_layout(showlegend=False); st.plotly_chart(fig_rank, use_container_width=True)
            with col_dir:
                st.subheader(f"📈 Resultados Diários ({mes_sel_nome})")
                if not df_mes.empty:
                    df_mes['Dia'] = df_mes['Data'].dt.day
                    evol = df_mes.groupby('Dia')['Valor'].sum().reset_index()
                    fig_lin = px.line(evol, x='Valor', y='Dia', orientation='h', markers=True, color_discrete_sequence=['#007a7c'])
                    st.plotly_chart(fig_lin, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            df_cv = pd.DataFrame(gc.get_worksheet(2).get_all_records())
            if not df_cv.empty:
                st.dataframe(df_cv, use_container_width=True)
            else:
                st.info("Nenhum currículo cadastrado na Aba 3 da planilha.")

        elif menu == "💰 Vendas":
            st.title("💰 Gestão de Vendas")
            st.dataframe(df_mes[['Data', 'Corretor', 'Valor', 'Tipo_Operacao', 'Comissão']], use_container_width=True)
            with st.expander("➕ Nova Operação"):
                with st.form("nova_venda"):
                    c_v = st.selectbox("Corretor", df_corr['Nome'].tolist() if not df_corr.empty else ["Nenhum"])
                    t_v = st.selectbox("Operação", list(TAXAS_COMISSAO.keys()))
                    v_v = st.number_input("Valor", min_value=0.0)
                    d_v = st.date_input("Data", value=datetime.now())
                    if st.form_submit_button("Confirmar"):
                        gc.get_worksheet(1).append_row([str(d_v), c_v, v_v, t_v])
                        st.success("Salvo!"); st.rerun()

        elif menu == "🧠 People Analytics":
            st.title("🧠 Inteligência de Equipe")
            if not df_corr.empty:
                fig_p = px.pie(df_corr, names='Especialidade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_p, use_container_width=True)

        elif menu == "👥 Corretores":
            st.title("👥 Banco de Dados")
            st.dataframe(df_corr, use_container_width=True)

    # --- TELA INICIAL ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>Enteder para atender.</p>", unsafe_allow_html=True)
        elif menu == "🔐 Acesso Restrito":
            u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"], st.session_state["user_logado"] = True, u; st.rerun()

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX | Atlas</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
