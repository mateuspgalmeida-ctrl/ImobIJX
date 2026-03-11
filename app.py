import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
from datetime import datetime
import re

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
META_MENSAL_LOJA = 50000.00
TAXAS_COMISSAO = {
    "Venda (Imóvel Novo/Planta)": 0.05,
    "Venda (Usado/Terceiros)": 0.06,
    "Aluguel (1º Aluguel Integral)": 1.00,
    "Administração Mensal": 0.10,
    "Consultoria/Avaliação": 0.20
}

MESES_PT = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 
            7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}

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
        padding: 15px; background-color: #fdf2f2; border-left: 5px solid #ec4899;
        border-radius: 4px; color: #9d174d; margin-bottom: 20px; font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO E CARREGAMENTO (COM CACHE) ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except Exception:
        return None

@st.cache_data(ttl=600)
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            return pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def limpar_moeda(valor):
    if isinstance(valor, str):
        valor = re.sub(r'[R\$\.\s]', '', valor).replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

def main():
    # Inicializa o estado de login se não existir
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # --- SIDEBAR ---
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
            
            st.divider()
            hoje = datetime.now()
            ano_sel = st.selectbox("Ano", [hoje.year, hoje.year-1], index=0)
            mes_sel_nome = st.selectbox("Mês", list(MESES_PT.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in MESES_PT.items() if v == mes_sel_nome][0]
            
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.session_state["user_logado"] = None
                st.rerun()

    # --- CARREGAMENTO DE DADOS ---
    df_corr = buscar_dados(0)
    df_vendas_raw = buscar_dados(1)
    
    if not df_vendas_raw.empty:
        df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
        df_vendas_raw['Valor'] = df_vendas_raw['Valor'].apply(limpar_moeda)
        df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
        df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
        df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

    # --- LÓGICA DAS TELAS ---
    if st.session_state["password_correct"]:
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard Estratégico {mes_sel_nome}/{ano_sel}")
            
            # --- TRATAMENTO SEGURO DE ANIVERSARIANTES ---
            if not df_corr.empty:
                df_corr.columns = [c.strip() for c in df_corr.columns]
                if 'Nascimento' in df_corr.columns:
                    df_corr['Mes_Nasc'] = pd.to_datetime(df_corr['Nascimento'], errors='coerce').dt.month
                    aniv = df_corr[df_corr['Mes_Nasc'] == datetime.now().month]['Nome'].tolist()
                    if aniv:
                        st.markdown(f'<div class="birthday-alert">🎂 <b>Aniversariantes do Mês:</b> {", ".join(aniv)}</div>', unsafe_allow_html=True)
            
            df_mes = df_vendas_raw[(df_vendas_raw['Ano'] == ano_sel) & (df_vendas_raw['Mes_Num'] == mes_sel_num)] if not df_vendas_raw.empty else pd.DataFrame()
            vgv_m = df_mes["Valor"].sum() if not df_mes.empty else 0
            perc_meta = min(vgv_m / META_MENSAL_LOJA, 1.0)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV {mes_sel_nome}</p><p class="kpi-val">R$ {vgv_m:,.2f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Meta da Loja</p><p class="kpi-val">{perc_meta:.1%}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Receita Est.</p><p class="kpi-val">R$ {df_mes["Comissão"].sum() if not df_mes.empty else 0:,.2f}</p></div>', unsafe_allow_html=True)
            
            st.progress(perc_meta, text=f"Progresso da Meta (Meta: R$ {META_MENSAL_LOJA:,.0f})")

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🏆 Ranking de VGV (Anual)")
                df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel] if not df_vendas_raw.empty else pd.DataFrame()
                if not df_ano.empty:
                    rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False)
                    fig = px.bar(rank, x='Corretor', y='Valor', color='Valor', text_auto='.2s', color_continuous_scale='Teal')
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                st.subheader(f"📈 Distribuição de Vendas")
                if not df_mes.empty:
                    fig_pie = px.pie(df_mes, values='Valor', names='Tipo_Operacao', hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            df_cv = buscar_dados(2)
            st.dataframe(df_cv, use_container_width=True)

    else: # TELAS PÚBLICAS
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.info("Utilize o menu lateral para acessar a área restrita.")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            with st.form("cadastro_cv", clear_on_submit=True):
                nome_cv = st.text_input("Nome Completo")
                tel_cv = st.text_input("Telefone/WhatsApp")
                exp_cv = st.selectbox("Experiência", ["Nenhuma", "Menos de 1 ano", "1 a 3 anos", "Mais de 3 anos"])
                obs_cv = st.text_area("Breve resumo profissional")
                if st.form_submit_button("Enviar Currículo"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([str(datetime.now().strftime('%d/%m/%Y %H:%M')), nome_cv, tel_cv, exp_cv, obs_cv])
                        st.success("Dados enviados com sucesso!")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Acesso ao Sistema")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            
            # O botão 'primary' e a ordem do rerun evitam o duplo clique
            if st.button("Acessar", type="primary"):
                try:
                    if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun() # Atualiza a página imediatamente após validar
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception:
                    st.error("Erro ao validar credenciais. Verifique o Secrets do Streamlit.")

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
