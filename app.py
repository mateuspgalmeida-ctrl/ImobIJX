import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(page_title="ImobIJX | Gestão de Talentos", layout="wide")

# 2. MOTOR DE ESTILO (CSS PARA FICAR IGUAL À IMAGEM)
st.markdown("""
    <style>
    /* Fundo da página e fontes */
    .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    
    /* Customização da Barra Lateral */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    
    /* Estilo dos Cards de KPIs */
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #007a7c;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Botões com a cor da marca */
    .stButton>button {
        background-color: #007a7c;
        color: white;
        border-radius: 10px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004d4d; color: white; border: none; }
    
    /* Ajuste de Títulos */
    h1, h2 { color: #004d4d; font-weight: 800; }
    .stMetric label { color: #666; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL PERSONALIZADA
with st.sidebar:
    try:
        st.image("logo.jpg", width=180)
    except:
        st.title("🏢 EmpImobIA")
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("MENU PRINCIPAL", 
        ["📊 Painel de Controle", "👥 Equipe Ativa", "🔍 Recrutamento", "🧠 Match Comportamental", "📈 Performance (VRIO)"])
    
    st.markdown("---")
    st.caption("Logado como Administrador")

# 4. CONTEÚDO DINÂMICO
if menu == "📊 Painel de Controle":
    st.title("KPIs da Imobiliária")
    st.markdown("---")
    
    # Linha de Cards (Igual à imagem)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Crescimento Equipe", "25", "+12%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Taxa de Retenção", "73%", "5%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Match Cultural", "6.0", "Ideal: 8.5")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Vendas do Mês", "R$ 1.2M", "+8%")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Área central de busca (O "Motor Atlas")
    st.subheader("Motor de Talento Atlas")
    with st.container():
        st.markdown('<div style="background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #e0e0e0;">', unsafe_allow_html=True)
        st.write("Busca de Corretores ou Metas:")
        c_a, c_b = st.columns([2, 1])
        with c_a:
            st.text_input("Filtrar por nome ou região...", label_visibility="collapsed")
        with c_b:
            st.button("Confirmar Busca")
        st.markdown('</div>', unsafe_allow_html=True)

    # Gráfico de Performance (Igual à imagem)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Destaques do Mês")
    chart_data = pd.DataFrame(
        np.random.rand(7, 3),
        columns=['Vendas', 'Captação', 'Atendimento']
    )
    st.area_chart(chart_data, color=["#007a7c", "#00b2b5", "#d1d5db"])

elif menu == "🧠 Match Comportamental":
    st.title("People Analytics")
    st.info("Insira os dados do candidato para o Atlas processar o Match.")
    # ... (lógica de match aqui)

# Rodapé minimalista
st.markdown("<br><hr><center>EmpImobIA v1.0 | Dashboard Estratégico</center>", unsafe_allow_html=True)
