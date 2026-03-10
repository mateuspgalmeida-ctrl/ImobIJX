import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="ImobIJX | Portal de Gestão", layout="wide", page_icon="🏢")

# --- TAXAS DE COMISSÃO CONFIGURÁVEIS ---
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
    except:
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

    # --- TELAS PÚBLICAS ---
    if not st.session_state["password_correct"]:
        if menu == "🏠 Início":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavir LTDA</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Entender para atender.</p>", unsafe_allow_html=True)
        elif menu == "💼 Carreira":
            st.title("🎯 Oportunidades ImobIJX")
            with st.form("cv_publico"):
                nome = st.text_input("Nome Completo")
                zap = st.text_input("WhatsApp")
                link = st.text_input("Link do Currículo")
                if st.form_submit_button("Candidatar-se"):
                    st.success("Candidatura enviada!")
        elif menu == "🔐 Acesso Restrito":
            st.title("🔐 Login")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()

    # --- TELAS ADMINISTRATIVAS ---
    else:
        gc = conecta_planilha()
        if not gc: return

        # Carregamento de Dados
        df_corr = pd.DataFrame(gc.get_worksheet(0).get_all_records())
        df_vendas = pd.DataFrame(gc.get_worksheet(1).get_all_records())

        # Tratamento de Dados
        if not df_corr.empty:
            df_corr['Nota_Performance'] = pd.to_numeric(df_corr['Nota_Performance'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        if not df_vendas.empty:
            df_vendas['Valor'] = pd.to_numeric(df_vendas['Valor'].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
            df_vendas['Comissão'] = df_vendas.apply(lambda x: x['Valor'] * TAXAS_COMISSAO.get(x['Tipo_Operacao'], 0.06), axis=1)

        if menu == "📊 Dashboard":
            st.title("📊 Painel de Controle")
            vgv = df_vendas['Valor'].sum() if not df_vendas.empty else 0
            receita = df_vendas['Comissão'].sum() if not df_vendas.empty else 0
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Time</p><p class="kpi-val">{len(df_corr)}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV Total</p><p class="kpi-val">R$ {vgv:,.2f}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Receita (Comissões)</p><p class="kpi-val">R$ {receita:,.2f}</p></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("🏆 Melhores do Mês (Top 3 Performance)")
            if not df_corr.empty:
                cols = st.columns(3)
                top3 = df_corr.sort_values(by='Nota_Performance', ascending=False).head(3)
                for i, row in enumerate(top3.itertuples()):
                    with cols[i]:
                        st.success(f"**{i+1}º {row.Nome}**\n\nNota: {row.Nota_Performance}")

        elif menu == "🧠 People Analytics":
            st.title("🧠 Inteligência e Match")
            
            # Match Inteligente
            tipo_imovel = st.selectbox("Buscar especialista para:", ["Luxo", "Rural", "Urbano", "Lançamentos"])
            sugeridos = df_corr[df_corr['Especialidade'] == tipo_imovel]
            if not sugeridos.empty:
                top = sugeridos.sort_values(by='Nota_Performance', ascending=False).iloc[0]
                st.info(f"💡 **Sugestão do Atlas:** O melhor perfil para esse imóvel é **{top['Nome']}**.")
            
            st.divider()
            col_a, col_b = st.columns([1, 1.5])
            with col_a:
                st.subheader("📊 Mix de Especialidades")
                st.bar_chart(df_corr['Especialidade'].value_counts(), color="#007a7c")
            with col_b:
                st.subheader("🔍 Raio-X Individual")
                nome_sel = st.selectbox("Selecionar Corretor:", df_corr['Nome'].unique())
                if nome_sel:
                    f = df_corr[df_corr['Nome'] == nome_sel].iloc[0]
                    st.write(f"**Especialidade:** {f.get('Especialidade', 'N/A')}")
                    st.progress(float(f.get('Nota_Performance', 0))/10)

        elif menu == "💰 Vendas":
            st.title("💰 Gestão Financeira")
            c_v1, c_v2 = st.columns([1, 2])
            with c_v1:
                with st.form("add_venda"):
                    st.subheader("Nova Operação")
                    corr = st.selectbox("Corretor", df_corr['Nome'].tolist())
                    tipo = st.selectbox("Tipo", list(TAXAS_COMISSAO.keys()))
                    val = st.number_input("Valor (R$)", min_value=0.0)
                    if st.form_submit_button("Registrar"):
                        gc.get_worksheet(1).append_row([str(datetime.now().date()), corr, val, tipo])
                        st.success("Registrado!")
                        st.rerun()
            with c_v2:
                st.subheader("Extrato")
                st.dataframe(df_vendas, use_container_width=True)

        elif menu == "👥 Corretores":
            st.title("👥 Gestão de Equipe")
            st.dataframe(df_corr, use_container_width=True)

    st.markdown("<p style='text-align: center; color: #cbd5e1; font-size: 11px;'>© 2026 ImobIJX | Atlas</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
