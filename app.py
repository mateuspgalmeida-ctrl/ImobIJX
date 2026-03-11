import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
import plotly.graph_objects as go
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

# --- ESTILO CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .birthday-alert {
        padding: 15px; background-color: #fdf2f2; border-left: 5px solid #ec4899;
        border-radius: 8px; color: #9d174d; margin-bottom: 20px; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (COM CACHE) ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

@st.cache_data(ttl=600) # Atualiza a cada 10 minutos
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            data = gc.get_worksheet(aba_index).get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def limpar_moeda(valor):
    """Converte 'R$ 1.200,50' ou '1200.50' em float puro."""
    if isinstance(valor, str):
        valor = re.sub(r'[R\$\.\s]', '', valor).replace(',', '.')
    try:
        return float(valor)
    except:
        return 0.0

# --- LÓGICA PRINCIPAL ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        
        st.divider()
        
        if not st.session_state["password_correct"]:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])
        else:
            st.success(f"Olá, {st.session_state.get('user_logado', 'Gestor')}")
            menu = st.radio("ADMINISTRAÇÃO", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            
            # Filtros de Data Globais para o Admin
            st.divider()
            hoje = datetime.now()
            ano_sel = st.selectbox("Ano de Referência", [hoje.year, hoje.year-1], index=0)
            mes_sel_nome = st.selectbox("Mês de Referência", list(MESES_PT.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in MESES_PT.items() if v == mes_sel_nome][0]
            
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- CARREGAMENTO E TRATAMENTO ---
    df_corr = buscar_dados(0)
    df_vendas_raw = buscar_dados(1)
    
    if not df_vendas_raw.empty:
        df_vendas_raw['Data'] = pd.to_datetime(df_vendas_raw['Data'], errors='coerce')
        df_vendas_raw['Valor'] = df_vendas_raw['Valor'].apply(limpar_moeda)
        df_vendas_raw['Ano'] = df_vendas_raw['Data'].dt.year
        df_vendas_raw['Mes_Num'] = df_vendas_raw['Data'].dt.month
        df_vendas_raw['Comissão'] = df_vendas_raw.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

    # --- RENDERIZAÇÃO DAS TELAS ---
    if st.session_state["password_correct"]:
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard {mes_sel_nome}/{ano_sel}")
            
            # Alerta de Aniversariantes
            if not df_corr.empty:
                df_corr['Mes_Nasc'] = pd.to_datetime(df_corr['Nascimento'], errors='coerce').dt.month
                aniv = df_corr[df_corr['Mes_Nasc'] == datetime.now().month]['Nome'].tolist()
                if aniv:
                    st.markdown(f'<div class="birthday-alert">🎂 <b>Aniversariantes do Mês:</b> {", ".join(aniv)}</div>', unsafe_allow_html=True)

            # Filtro dos dados para o Dashboard
            df_mes = df_vendas_raw[(df_vendas_raw['Ano'] == ano_sel) & (df_vendas_raw['Mes_Num'] == mes_sel_num)]
            vgv_m = df_mes["Valor"].sum()
            receita_m = df_mes["Comissão"].sum()
            progresso = vgv_m / META_MENSAL_LOJA

            # KPIs Modernos
            c1, c2, c3 = st.columns(3)
            c1.metric("VGV Total", f"R$ {vgv_m:,.2f}", delta=f"{progresso:.1%} da meta")
            c2.metric("Receita Estimada", f"R$ {receita_m:,.2f}")
            c3.metric("Ticket Médio", f"R$ {(vgv_m/len(df_mes) if len(df_mes)>0 else 0):,.2f}")

            st.progress(min(progresso, 1.0), text=f"Progresso da Meta: R$ {vgv_m:,.2f} / R$ {META_MENSAL_LOJA:,.2f}")

            st.divider()
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("🏆 Ranking de Corretores (Ano)")
                df_ano = df_vendas_raw[df_vendas_raw['Ano'] == ano_sel]
                if not df_ano.empty:
                    rank = df_ano.groupby('Corretor')['Valor'].sum().reset_index().sort_values('Valor', ascending=True)
                    fig = px.bar(rank, x='Valor', y='Corretor', orientation='h', color='Valor', 
                                 color_continuous_scale='Tealgrn', text_auto='.2s')
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.subheader("🍕 Tipos de Operação")
                if not df_mes.empty:
                    fig_pie = px.pie(df_mes, values='Valor', names='Tipo_Operacao', hole=0.4,
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            df_cv = buscar_dados(2)
            st.dataframe(df_cv, use_container_width=True, height=500)

    else: # TELAS PÚBLICAS
        if menu == "🏠 Início":
            st.markdown("<div style='text-align: center; padding: 50px 0;'>", unsafe_allow_html=True)
            st.title("Imobiliária Janeide Xavier LTDA")
            st.write("Entender para atender.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.info("🏢 **Locação**\nGestão completa de contratos.")
            c2.success("🔑 **Vendas**\nNovos, usados e na planta.")
            c3.warning("📊 **Avaliação**\nPerícia técnica de imóveis.")

        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            with st.form("cadastro_cv", clear_on_submit=True):
                nome_cv = st.text_input("Nome Completo")
                tel_cv = st.text_input("Telefone/WhatsApp")
                exp_cv = st.selectbox("Experiência no Ramo", ["Nenhuma", "Menos de 1 ano", "1 a 3 anos", "Mais de 3 anos"])
                obs_cv = st.text_area("Fale um pouco sobre você")
                
                if st.form_submit_button("Enviar Cadastro"):
                    if nome_cv and tel_cv:
                        gc = conecta_planilha()
                        gc.get_worksheet(2).append_row([str(datetime.now().strftime('%d/%m/%Y %H:%M')), nome_cv, tel_cv, exp_cv, obs_cv])
                        st.success("Cadastro realizado! Nossa equipe entrará em contato.")
                    else:
                        st.error("Por favor, preencha Nome e Telefone.")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Acesso Administrativo")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                try:
                    if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")
                except:
                    st.error("Erro ao validar credenciais. Verifique o secrets.toml.")

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
