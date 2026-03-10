import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
from datetime import datetime

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
META_MENSAL_LOJA = 50000.00  # Exemplo de meta de VGV mensal
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
    .birthday-alert {
        padding: 10px; background-color: #fdf2f2; border-left: 5px solid #ec4899;
        border-radius: 4px; color: #9d174d; margin-bottom: 20px;
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
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])
        else:
            st.success(f"Logado: {st.session_state.get('user_logado', 'Gestor')}")
            menu = st.radio("ADMINISTRAÇÃO", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()

    gc = conecta_planilha()
    if not gc: 
        st.error("Erro ao conectar com a base de dados.")
        return

    # --- CARREGAMENTO DE DADOS ---
    df_corr = pd.DataFrame(gc.get_worksheet(0).get_all_records())
    df_vendas_raw = pd.DataFrame(gc.get_worksheet(1).get_all_records())
    
    hoje = datetime.now()
    meses_pt = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    
    # Tratamento de Vendas
    df_ano, df_mes = pd.DataFrame(), pd.DataFrame()
    ano_sel, mes_sel_nome = hoje.year, meses_pt[hoje.month]

    if not df_vendas_raw.empty:
        df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
        df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
        df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
        df_vendas_raw['Valor'] = pd.to_numeric(df_vendas_raw['Valor'].astype(str).str.replace('R$', '').replace('.', '').replace(',', '.'), errors='coerce').fillna(0)
        df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

        if st.session_state["password_correct"]:
            st.sidebar.divider()
            anos_disp = sorted([int(a) for a in df_vendas_raw['Ano'].dropna().unique()], reverse=True)
            ano_sel = st.sidebar.selectbox("Ano", anos_disp if anos_disp else [hoje.year])
            mes_sel_nome = st.sidebar.selectbox("Mês", list(meses_pt.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in meses_pt.items() if v == mes_sel_nome][0]
            df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel]
            df_mes = df_ano[df_ano['Mes_Num'] == mes_sel_num]

    # --- LÓGICA DAS TELAS ---
    if st.session_state["password_correct"]:
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard Estratégico {ano_sel}")
            
            # Alerta de Aniversariantes
            if not df_corr.empty and 'Nascimento' in df_corr.columns:
                df_corr['Mes_Nasc'] = pd.to_datetime(df_corr['Nascimento'], errors='coerce').dt.month
                aniversariantes = df_corr[df_corr['Mes_Nasc'] == hoje.month]['Nome'].tolist()
                if aniversariantes:
                    st.markdown(f'<div class="birthday-alert">🎂 <b>Aniversariantes de {meses_pt[hoje.month]}:</b> {", ".join(aniversariantes)}</div>', unsafe_allow_html=True)

            vgv_m = df_mes["Valor"].sum() if not df_mes.empty else 0
            perc_meta = min(vgv_m / META_MENSAL_LOJA, 1.0)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV {mes_sel_nome}</p><p class="kpi-val">R$ {vgv_m:,.2f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Meta da Loja</p><p class="kpi-val">{perc_meta:.1%}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Receita Est.</p><p class="kpi-val">R$ {df_mes["Comissão"].sum() if not df_mes.empty else 0:,.2f}</p></div>', unsafe_allow_html=True)
            
            st.progress(perc_meta, text=f"Progresso da Meta Mensal (R$ {META_MENSAL_LOJA:,.0f})")

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🏆 Ranking de VGV (Anual)")
                if not df_ano.empty:
                    rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False)
                    fig = px.bar(rank, x='Corretor', y='Valor', color='Corretor', text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Prism)
                    fig.update_layout(showlegend=False); st.plotly_chart(fig, use_container_width=True)
            with col_b:
                st.subheader(f"📈 Fluxo de Vendas em {mes_sel_nome}")
                if not df_mes.empty:
                    df_mes['Dia'] = df_mes['Data'].dt.day
                    evol = df_mes.groupby('Dia')['Valor'].sum().reset_index()
                    fig_l = px.line(evol, x='Valor', y='Dia', orientation='h', markers=True, color_discrete_sequence=['#007a7c'])
                    st.plotly_chart(fig_l, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            df_cv = pd.DataFrame(gc.get_worksheet(2).get_all_records())
            st.dataframe(df_cv, use_container_width=True)

        # (Outros módulos ADMIN: People Analytics, Corretores, Vendas permanecem iguais à v3.2)

    else: # TELAS PÚBLICAS
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Bem-vindo ao portal de gestão da Imobiliária Janete Xavier.</h3>", unsafe_allow_html=True)
            st.info("Utilize o menu lateral para navegar ou acessar a área restrita.")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            st.write("Cadastre seus dados para futuras oportunidades em Feira de Santana.")
            with st.form("cadastro_cv"):
                nome_cv = st.text_input("Nome Completo")
                tel_cv = st.text_input("Telefone/WhatsApp")
                exp_cv = st.selectbox("Experiência", ["Nenhuma", "Menos de 1 ano", "1 a 3 anos", "Mais de 3 anos"])
                obs_cv = st.text_area("Breve resumo profissional")
                if st.form_submit_button("Enviar Currículo"):
                    gc.get_worksheet(2).append_row([str(datetime.now()), nome_cv, tel_cv, exp_cv, obs_cv])
                    st.success("Dados enviados com sucesso! Entraremos em contato.")

        elif menu == "🔐 Painel Restrito":
            u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"], st.session_state["user_logado"] = True, u; st.rerun()

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
