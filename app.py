# --- ADICIONE '🧠 People Analytics' AO SEU RADIO DE MENU ---
# menu = st.radio("PAINEL ADMIN", ["📊 Dashboard", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])

if menu == "🧠 People Analytics":
    st.title("🧠 People Analytics & Talent Intelligence")
    st.markdown("---")
    
    gc = conecta_planilha()
    if gc:
        # Puxa os dados da Aba 1 (Corretores)
        sheet_corr = gc.get_worksheet(0)
        df = pd.DataFrame(sheet_corr.get_all_records())
        
        if not df.empty:
            # 1. VISÃO GERAL DA EQUIPE (KPIs de RH)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Total Equipe</p><p class="kpi-val">{len(df)}</p></div>', unsafe_allow_html=True)
            with c2:
                nota_media = df['Nota_Performance'].mean() if 'Nota_Performance' in df.columns else 0
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Média Performance</p><p class="kpi-val">{nota_media:.1f}/10</p></div>', unsafe_allow_html=True)
            with c3:
                perfil_dom = df['Perfil'].mode()[0] if 'Perfil' in df.columns else "N/A"
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Perfil Dominante</p><p class="kpi-val">{perfil_dom}</p></div>', unsafe_allow_html=True)
            with c4:
                # Skill mais frequente
                skill_dom = df['Habilidade_Principal'].mode()[0] if 'Habilidade_Principal' in df.columns else "N/A"
                st.markdown(f'<div class="kpi-card"><p class="kpi-label">Skill Principal</p><p class="kpi-val">{skill_dom}</p></div>', unsafe_allow_html=True)

            st.write("<br>", unsafe_allow_html=True)

            # 2. GRÁFICOS DE ANÁLISE CRUZADA
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                st.subheader("📊 Mix Comportamental")
                st.bar_chart(df['Perfil'].value_counts(), color="#007a7c")
            
            with col_graph2:
                st.subheader("🎯 Matriz de Habilidades")
                st.bar_chart(df['Habilidade_Principal'].value_counts(), color="#2e4d4d")

            st.divider()

            # 3. O "MATCH" DO ATLAS (INTELIGÊNCIA ARTIFICIAL)
            st.subheader("🔍 Recomendação de Alocação Estratégica")
            col_sim1, col_sim2 = st.columns([1, 2])
            
            with col_sim1:
                st.info("Simule o melhor corretor para um cenário:")
                cenario = st.selectbox("Cenário de Venda:", [
                    "Imóvel de Luxo (Exige Networking)",
                    "Fechamento Rápido (Exige Foco)",
                    "Contrato Complexo (Exige Detalhe)",
                    "Pós-Venda/Relacionamento"
                ])
            
            with col_sim2:
                if cenario == "Imóvel de Luxo (Exige Networking)":
                    st.success("💡 **Recomendação do Atlas:** Busque perfis **Comunicadores**. Eles possuem maior facilidade em transitar em ambientes de alto padrão.")
                elif cenario == "Fechamento Rápido (Exige Foco)":
                    st.success("💡 **Recomendação do Atlas:** Aloque um **Executor**. O foco em metas e a velocidade de resposta são essenciais aqui.")
                elif cenario == "Contrato Complexo (Exige Detalhe)":
                    st.success("💡 **Recomendação do Atlas:** Perfis **Analíticos** são ideais para revisar cláusulas e garantir segurança jurídica.")
                else:
                    st.success("💡 **Recomendação do Atlas:** Perfis **Planejadores** mantêm a organização e a satisfação do cliente a longo prazo.")

            # 4. TABELA DE TALENTOS FILTRÁVEL
            st.write("<br>", unsafe_allow_html=True)
            st.subheader("📋 Base de Talentos")
            filtros = st.multiselect("Filtrar por Habilidade Técnica:", options=df['Habilidade_Principal'].unique())
            if filtros:
                st.dataframe(df[df['Habilidade_Principal'].isin(filtros)], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Aguardando dados para gerar inteligência...")

# --- LEMBRE-SE DE ATUALIZAR O FORMULÁRIO DE CADASTRO PARA INCLUIR ESTES NOVOS CAMPOS ---
