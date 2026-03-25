import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import io

# --- 1. CONFIGURAÇÃO DE PÁGINA (Layout Wide para Máxima Visão) ---
st.set_page_config(page_title="ImobIJX | Master Intelligence ERP", layout="wide", page_icon="🏢")

# --- 2. CONFIGURAÇÕES DE NEGÓCIO ---
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
BAIRROS_FEIRA = ["SIM", "Santa Mônica", "Papagaio", "Noide Cerqueira", "Kalilândia", "Centro", "Muchila", "Tomba", "Outros"]
DIAS_LIMITE_PARADO = 10  # Regra de Ouro: 10 dias sem movimento = Alerta!

# --- 3. ESTILO CSS CUSTOMIZADO (Interface Premium) ---
st.markdown("""
    <style>
    /* Fundo e Fonte Global */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Cartões KPI Estilizados */
    .kpi-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        border-top: 5px solid #007a7c; text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-5px); }
    .kpi-label { color: #64748b; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-val { color: #0f172a; font-size: 2.5rem; font-weight: 800; margin-top: 10px; }
    
    /* Mural Master Premium */
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 30px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin-bottom: 30px;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
    }
    .mural-master h3 { color: #fbbf24; font-weight: 800; }
    .mural-master p { color: #e2e8f0; font-size: 1.1rem; }
    
    /* Badges de Usuário */
    .master-badge { background-color: #1e293b; color: #fbbf24; padding: 5px 15px; border-radius: 8px; font-size: 12px; font-weight: 800; border: 1px solid #fbbf24; }
    .admin-badge { background-color: #007a7c; color: white; padding: 5px 15px; border-radius: 8px; font-size: 12px; font-weight: 600; }
    
    /* Alertas de Leads Parados */
    .alerta-box {
        background-color: #fff1f2; border-left: 5px solid #e11d48;
        padding: 20px; border-radius: 10px; color: #9f1239; font-weight: 700; font-size: 1.1rem; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS E CONEXÃO ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("Dados_ImobIJX")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

@st.cache_data(ttl=300)
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            df = pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

# --- 5. LÓGICA DE ALERTAS ---
def identificar_leads_parados(df):
    if df.empty: return pd.DataFrame()
    hoje = datetime.now()
    limite = hoje - timedelta(days=DIAS_LIMITE_PARADO)
    # Filtra apenas quem ainda é Lead ou Potencial e não se mexe há X dias
    parados = df[(df['Status'].isin(['Lead', 'Cliente Potencial'])) & (df['Data'] <= limite)]
    return parados

# --- 6. MAIN APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # --- 7. SIDEBAR (Com Logo e Identificação Restauradas) ---
    with st.sidebar:
        # Tenta carregar a logo, se não houver, usa o nome estilizado
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h1>", unsafe_allow_html=True)
        
        st.divider()
        
        if st.session_state["password_correct"]:
            user_logado = st.session_state.get('user_logado', '').lower()
            
            # Identificação visual do nível de acesso
            if user_logado == "mateus":
                st.markdown(f"👑 **{user_logado.upper()}** <br><span class='master-badge'>MASTER ACCESS</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"👤 **{user_logado.upper()}** <br><span class='admin-badge'>ADMINISTRATIVO</span>", unsafe_allow_html=True)
            
            st.write("")
            # Menu completo e estratégico para os três
            menu = st.radio("SISTEMA GESTÃO", [
                "🏛️ Mural Master", 
                "📊 Dashboard Geral", 
                "🔥 Zonas de Calor",
                "🤝 CRM Clientes", 
                "🏆 Ranking Performance", 
                "🧠 People Analytics", 
                "👥 Equipe Corretores", 
                "💰 Vendas", 
                "📄 Banco de Talentos"
            ])
            
            # Ferramentas exclusivas do Master (Mateus)
            if user_logado == "mateus":
                st.divider()
                st.subheader("🛠 Ferramentas Master")
                if st.button("📥 Gerar Backup Excel"):
                    # Lógica simplificada de backup (pode ser expandida)
                    st.success("Backup preparado! (Simulação)")

            st.divider()
            if st.button("🚪 Sair do Sistema"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])

    # --- 8. CARGA DE DADOS PARA TELAS ---
    df_corr = buscar_dados(0)
    df_vendas = buscar_dados(1)
    df_cv = buscar_dados(2)
    df_clientes = buscar_dados(3)

    # --- 9. TELAS ADMINISTRATIVAS (ACESSO TOTAL MATEUS/JANEIDE/GESSICA) ---
    if st.session_state["password_correct"]:
        user_logado = st.session_state.get('user_logado', '').lower()

        if menu == "🏛️ Mural Master":
            st.title("🏛️ Mural de Avisos Master")
            st.markdown(f"""
                <div class="mural-master">
                    <h3>📢 Metas e Alinhamento Estratégico - Março 2026</h3>
                    <p><b>1. ZONAS DE CALOR:</b> Foco total em captações no <b>SIM</b> e <b>Noide Cerqueira</b>. Os dados mostram que a demanda está lá.</p>
                    <p><b>2. LIMPEZA CRM:</b> Atacar a lista de "Leads Parados" (+10 dias). Cobrem agilidade dos corretores!</p>
                    <p><b>3. RECRUTAMENTO:</b> Use nosso ERP Inteligente como argumento para atrair corretores "tubarões". Mostre que aqui a tecnologia trabalha para eles.</p>
                    <br>
                    <p><i>"Onde há dados, há clareza. Onde há clareza, há fechamento. Vamos para cima!" - Master Mateus</i></p>
                </div>
            """, unsafe_allow_html=True)
            st.info("Apenas Mateus, Janeide e Gessica visualizam este painel.")

        elif menu == "📊 Dashboard Geral":
            st.title(f"📊 Dashboard Estratégico - ImobIJX")
            
            # Alerta de Leads Parados no Topo
            leads_parados = identificar_leads_parados(df_clientes)
            if not leads_parados.empty:
                st.markdown(f'<div class="alerta-box">⚠️ ATENÇÃO: Existem {len(leads_parados)} leads sem movimentação há mais de {DIAS_LIMITE_PARADO} dias! Verifiquem a aba CRM imediamente.</div>', unsafe_allow_html=True)
            
            # KPIs Principais
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Base CRM</p><p class="kpi-val">{len(df_clientes)}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Leads Novos (Mês)</p><p class="kpi-val">{len(df_clientes[df_clientes["Status"]=="Lead"])}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Vendas Registradas</p><p class="kpi-val">{len(df_vendas)}</p></div>', unsafe_allow_html=True)
            
            # Funil de Vendas
            if not df_clientes.empty:
                st.divider()
                funil_data = df_clientes['Status'].value_counts().reindex(STATUS_CLIENTE).fillna(0)
                st.plotly_chart(px.funnel(x=funil_data.values, y=funil_data.index, title="Funil de Conversão ImobIJX", color_discrete_sequence=['#007a7c']), use_container_width=True)

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor - Feira de Santana")
            st.write("Análise visual da demanda imobiliária por bairro.")
            
            if not df_clientes.empty and 'Bairro' in df_clientes.columns:
                # Mapa de Calor Simplificado (Gráfico de Barras com Gradiente)
                heat_data = df_clientes['Bairro'].value_counts().reset_index()
                heat_data.columns = ['Bairro', 'Volume de Leads']
                
                fig_heat = px.bar(heat_data, x='Bairro', y='Volume de Leads', color='Volume de Leads', 
                                 title="Volume de Demanda por Bairro",
                                 color_continuous_scale='OrRd', template='plotly_white')
                st.plotly_chart(fig_heat, use_container_width=True)
                
                # KPIs de Região
                c1, c2 = st.columns(2)
                with c1:
                    bairro_quente = heat_data.iloc[0]['Bairro'] if not heat_data.empty else "N/A"
                    st.metric("Bairro mais Quente", bairro_quente)
                with c2:
                    st.metric("Total de Bairros Ativos", len(heat_data))
                    
                st.info("Regra Estratégica: Focar captações e anúncios nos bairros mais 'quentes' (vermelhos) para acelerar o VGV.")
            else:
                st.warning("Cadastre o 'Bairro' nos seus leads para começar a visualizar as zonas de calor.")

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 Gestão de Relacionamento (CRM)")
            leads_parados = identificar_leads_parados(df_clientes)
            
            tab_base, tab_parados, tab_novo = st.tabs(["📋 Base Completa", "🚨 Leads Parados (+10 dias)", "➕ Novo Cadastro"])
            
            with tab_base:
                st.dataframe(df_clientes, use_container_width=True)
            
            with tab_parados:
                if not leads_parados.empty:
                    st.warning(f"Existem {len(leads_parados)} clientes que precisam de contato urgente.")
                    st.dataframe(leads_parados[['Data', 'Nome', 'Status', 'Bairro', 'Corretor']], use_container_width=True)
                else:
                    st.success("Parabéns! Nenhum lead parado no momento. Gestão eficiente!")
            
            with tab_novo:
                with st.form("form_crm"):
                    n = st.text_input("Nome do Cliente")
                    b = st.selectbox("Bairro de Interesse (Feira de Santana)", BAIRROS_FEIRA)
                    s = st.selectbox("Status Atual", STATUS_CLIENTE)
                    corr = st.selectbox("Corretor Responsável", df_corr['Nome'].unique() if not df_corr.empty else ["Gestão"])
                    if st.form_submit_button("Cadastrar no Sistema"):
                        gc = conecta_planilha()
                        # Append na aba de clientes (index 3)
                        gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), n, "", s, b, "Portal", corr])
                        st.success(f"Cliente registrado com sucesso por {st.session_state['user_logado']}!")
                        st.cache_data.clear()
                        st.rerun()

        elif menu == "🏆 Ranking Performance":
            st.title("🏆 Ranking de Performance da Equipe")
            if not df_clientes.empty:
                ranking = df_clientes['Corretor'].value_counts().reset_index()
                ranking.columns = ['Corretor', 'Total Leads']
                
                st.plotly_chart(px.pie(ranking, values='Total Leads', names='Corretor', title="Distribuição da Carteira de Leads"), use_container_width=True)
                
                st.subheader("Eficiência e Cobrança")
                parados_ranking =
