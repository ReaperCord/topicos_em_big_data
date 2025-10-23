import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.preprocessing import MinMaxScaler # Para o KPI 4

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Analítico de Risco",
    page_icon="📊",
    layout="wide"
)

# --- TEMA CLARO PARA GRÁFICOS ---
# Força o Plotly a usar um tema claro (fundo branco, texto preto)
px.defaults.template = "plotly_white"

# --- Carregamento e Processamento de Dados (CSV Local) ---
@st.cache_data
def load_data():
    """
    Carrega os dados dos dois arquivos CSV (com separador ';'),
    cria a coluna 'perfil_risco' e calcula os KPIs.
    """
    
    # --- 1. Nomes dos Arquivos ATUALIZADOS com o caminho ./data/ ---
    FILE_TEMPORAL = "./data/gold_dashboard_data.csv"
    FILE_PERFIS = "./data/perfis_de_risco_k6.csv" # <--- AJUSTE O 'k6' SE NECESSÁRIO
    
    try:
        df_temporal = pd.read_csv(FILE_TEMPORAL, sep=';')
        df_perfis = pd.read_csv(FILE_PERFIS, sep=';')
    except FileNotFoundError as e:
        st.error(f"Erro: Arquivo não encontrado: {e.filename}")
        st.error(f"Por favor, certifique-se de que `{FILE_TEMPORAL}` e `{FILE_PERFIS}` estão na pasta ./data/.")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler os arquivos CSV: {e}")
        return pd.DataFrame(), pd.DataFrame()

    if 'cluster_id' not in df_perfis.columns:
        st.error(f"Coluna 'cluster_id' não encontrada em `{FILE_PERFIS}`.")
        return pd.DataFrame(), pd.DataFrame()
    df_perfis['perfil_risco'] = 'Cluster ' + df_perfis['cluster_id'].astype(str)

    if 'cluster_id' not in df_temporal.columns:
        st.error(f"Coluna 'cluster_id' não encontrada em `{FILE_TEMPORAL}`.")
        return pd.DataFrame(), pd.DataFrame()
    
    perfil_labels = df_perfis[['cluster_id', 'perfil_risco']].drop_duplicates()
    df_temporal = pd.merge(df_temporal, perfil_labels, on='cluster_id', how='left')

    # Validação Mínima
    colunas_temporal_req = ['ano', 'mes', 'aisp', 'cluster_id', 'perfil_risco', 'recuperacao_veiculos', 'roubo_veiculo', 'total_roubos', 'total_furtos', 'roubo_rua']
    for col in colunas_temporal_req:
        if col not in df_temporal.columns:
            st.warning(f"Coluna `{col}` não encontrada em `{FILE_TEMPORAL}`. Gráficos relacionados podem falhar ou mostrar 0.")
            df_temporal[col] = 0 # Adiciona coluna com 0 para evitar quebra

    colunas_perfis_req = ['cluster_id', 'perfil_risco', 'armas_arma_fogo_fuzil', 'letalidade_violenta', 'hom_por_interv_policial', 'estupro', 'fem_feminicidio', 'roubo_rua', 'roubo_veiculo', 'roubo_carga', 'n_de_aisps']
    for col in colunas_perfis_req:
         if col not in df_perfis.columns:
            st.warning(f"Coluna `{col}` não encontrada em `{FILE_PERFIS}`. Gráficos relacionados podem falhar ou mostrar 0.")
            df_perfis[col] = 0 # Adiciona coluna com 0 para evitar quebra
            
    # --- Cálculo do KPI 4: Matriz de Risco ---
    vida_cols = ['letalidade_violenta', 'estupro', 'fem_feminicidio']
    patrim_cols = ['roubo_rua', 'roubo_veiculo', 'roubo_carga']
    cols_to_scale = list(set(vida_cols + patrim_cols))

    scaler = MinMaxScaler()
    df_perfis_calculado = df_perfis.copy()
    
    cols_existentes = [col for col in cols_to_scale if col in df_perfis_calculado.columns]
    if len(cols_existentes) > 0:
        df_perfis_calculado[cols_existentes] = scaler.fit_transform(df_perfis_calculado[cols_existentes])
    
    # Adicionado .fillna(0) para garantir que não haja NaNs
    df_perfis_calculado['Indice_Vida'] = df_perfis_calculado[[col for col in vida_cols if col in df_perfis_calculado.columns]].mean(axis=1).fillna(0)
    df_perfis_calculado['Indice_Patrimonio'] = df_perfis_calculado[[col for col in patrim_cols if col in df_perfis_calculado.columns]].mean(axis=1).fillna(0)
    
    # --- Cálculo do KPI 6: Proporção de Confronto ---
    df_perfis_calculado['Proporcao_Confronto'] = (
        df_perfis_calculado['hom_por_interv_policial'] / 
        df_perfis_calculado['letalidade_violenta'].replace(0, np.nan) 
    ).fillna(0) * 100

    return df_temporal, df_perfis_calculado

# --- Carregar Dados ---
df_temporal, df_perfis = load_data()

if df_temporal.empty or df_perfis.empty:
    st.stop()

# --- BARRA LATERAL (Filtros Globais) ---
perfis_disponiveis = sorted(df_perfis['perfil_risco'].unique())
anos_disponiveis = sorted(df_temporal['ano'].unique())

st.sidebar.title("Filtros do Dashboard")
st.sidebar.info("Use os filtros abaixo para analisar os perfis de risco.")

ano_filtro = st.sidebar.slider(
    "Selecione o(s) Ano(s)",
    min_value=min(anos_disponiveis),
    max_value=max(anos_disponiveis),
    value=(min(anos_disponiveis), max(anos_disponiveis))
)

perfil_filtro = st.sidebar.multiselect(
    "Filtre por Perfil de Risco (Cluster)",
    options=perfis_disponiveis,
    default=perfis_disponiveis
)

# --- Lógica de Filtragem ---
df_temp_filtrado = df_temporal[
    (df_temporal['ano'] >= ano_filtro[0]) & (df_temporal['ano'] <= ano_filtro[1]) &
    (df_temporal['perfil_risco'].isin(perfil_filtro))
]
df_perf_filtrado = df_perfis[
    df_perfis['perfil_risco'].isin(perfil_filtro)
]

# --- ÁREA DE CONTEÚDO PRINCIPAL ---
st.title("Dashboard Analítico de Segurança Pública")
st.markdown(f"Analisando dados de **{ano_filtro[0]}** a **{ano_filtro[1]}**.")

if df_temp_filtrado.empty or df_perf_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste os filtros.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendência & Nível de Ameaça", 
    "🛡️ Eficácia & Perfil do Crime", 
    "🗺️ Matriz de Risco Resumido",
    "🔎 Detalhe por Cluster" # <-- ABA ATUALIZADA
])

# --- ABA 1: Tendência & Nível de Ameaça ---
with tab1:
    st.info("**KPI 5: O Risco Está Mudando?** e **KPI 2: Qual o Nível da Ameaça?**")
    
    col1, col2 = st.columns([2, 1]) 
    with col1:
        st.subheader("Evolução do Risco (Total de Roubos de Rua)")
        
        df_evolucao = df_temp_filtrado.groupby(['ano', 'mes', 'perfil_risco'])['roubo_rua'].sum().reset_index()
        df_evolucao['data'] = pd.to_datetime(df_evolucao[['ano', 'mes']].assign(day=1).rename(columns={'ano': 'year', 'mes': 'month'}))
        df_evolucao = df_evolucao.sort_values(by='data')
        
        fig_linha = px.line(
            df_evolucao, x='data', y='roubo_rua', color='perfil_risco',
            title="Evolução do Total de Roubos de Rua por Perfil",
            labels={'data': 'Data', 'roubo_rua': 'Total de Roubos de Rua', 'perfil_risco': 'Perfil de Risco'}
        )
        st.plotly_chart(fig_linha, use_container_width=True)
        
    with col2:
        st.subheader("Nível de Ameaça (Média de Fuzis)")
        
        fig_fuzil = px.bar(
            df_perf_filtrado.sort_values('armas_arma_fogo_fuzil', ascending=False),
            x='perfil_risco', y='armas_arma_fogo_fuzil',
            title="Média de Fuzis Apreendidos por Perfil",
            labels={'perfil_risco': 'Perfil de Risco', 'armas_arma_fogo_fuzil': 'Média de Fuzis Apreendidos'},
            color='perfil_risco', text_auto='.2f'
        )
        st.plotly_chart(fig_fuzil, use_container_width=True)

# --- ABA 2: Eficácia & Perfil do Crime ---
with tab2:
    st.info("**KPI 1: A Resposta está Funcionando?** e **KPI 3 & 6: Qual o Perfil da Violência?**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Eficácia: Taxa de Recuperação de Veículos")
        
        df_recup_agg = df_temp_filtrado.groupby('perfil_risco')[['recuperacao_veiculos', 'roubo_veiculo']].sum().reset_index()
        df_recup_agg['taxa_recuperacao'] = (
            df_recup_agg['recuperacao_veiculos'] / 
            df_recup_agg['roubo_veiculo'].replace(0, np.nan)
        ).fillna(0)
        
        fig_recup = px.bar(
            df_recup_agg.sort_values('taxa_recuperacao', ascending=False),
            x='perfil_risco', y='taxa_recuperacao',
            title="Taxa de Recuperação de Veículos por Perfil",
            labels={'perfil_risco': 'Perfil de Risco', 'taxa_recuperacao': 'Taxa de Recuperação'},
            color='perfil_risco', text_auto='.1%'
        )
        fig_recup.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_recup, use_container_width=True)

    with col2:
        st.subheader("Perfil: Proporção Roubo vs. Furto")
        
        df_prop_agg = df_temp_filtrado.groupby('perfil_risco')[['total_roubos', 'total_furtos']].sum().reset_index()
        df_prop_agg['proporcao_roubo_furto'] = (
            df_prop_agg['total_roubos'] / 
            df_prop_agg['total_furtos'].replace(0, np.nan)
        ).fillna(0)
        
        fig_prop = px.bar(
            df_prop_agg.sort_values('proporcao_roubo_furto', ascending=False),
            x='perfil_risco', y='proporcao_roubo_furto',
            title="Proporção Roubo x Furto por Perfil",
            labels={'perfil_risco': 'Perfil de Risco', 'proporcao_roubo_furto': 'Proporção (Roubos / Furtos)'},
            color='perfil_risco', text_auto='.1f'
        )
        st.plotly_chart(fig_prop, use_container_width=True)
    
    st.divider()
    
    st.subheader("Perfil: Proporção de Letalidade por Intervenção Policial")
    
    fig_confronto = px.bar(
        df_perf_filtrado.sort_values('Proporcao_Confronto', ascending=False),
        x='perfil_risco', y='Proporcao_Confronto',
        title="Participação da Intervenção Policial na Letalidade Violenta",
        labels={'perfil_risco': 'Perfil de Risco', 'Proporcao_Confronto': '% da Letalidade por Intervenção'},
        color='perfil_risco', text_auto='.1f'
    )
    fig_confronto.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_confronto, use_container_width=True)


# --- ABA 3: Matriz de Risco Resumido ---
with tab3:
    st.info("**KPI 4: O Risco Resumido.** Este gráfico é uma visualização estratégica do posicionamento de cada cluster.")
    
    st.subheader("Matriz de Risco (Patrimônio vs. Vida)")
    
    media_vida = df_perf_filtrado['Indice_Vida'].mean()
    media_patrimonio = df_perf_filtrado['Indice_Patrimonio'].mean()
    
    # --- TENTATIVA DE CORREÇÃO ---
    # Adicionado color='perfil_risco' para criar traces separados por cluster
    # Isso é mais robusto para garantir que os marcadores sejam desenhados
    fig_matrix = px.scatter(
        df_perf_filtrado,
        x='Indice_Patrimonio', y='Indice_Vida',
        text='perfil_risco',
        color='perfil_risco', # <-- Força a criação de traces
        title="Matriz de Risco: Vida vs. Patrimônio (Índices Normalizados)",
        labels={
            'Indice_Patrimonio': 'Índice de Risco Patrimonial (Normalizado)',
            'Indice_Vida': 'Índice de Risco à Vida (Normalizado)'
        },
        hover_data={'perfil_risco': True, 'Indice_Patrimonio': ':.3f', 'Indice_Vida': ':.3f'}
    )
    
    # Adicionado mode='markers+text' para garantir que os pontos E o texto apareçam
    fig_matrix.update_traces(textposition='top center', textfont_size=12, marker_size=15, mode='markers+text')
    # --- FIM DA TENTATIVA DE CORREÇÃO ---

    fig_matrix.add_vline(x=media_patrimonio, line_width=2, line_dash="dash", line_color="gray", annotation_text="Média Risco Patrimônio")
    fig_matrix.add_hline(y=media_vida, line_width=2, line_dash="dash", line_color="gray", annotation_text="Média Risco à Vida")
    
    fig_matrix.add_annotation(x=media_patrimonio*1.01, y=media_vida*1.01, text="Alto Risco (Ambos)", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color="red", size=12))
    fig_matrix.add_annotation(x=media_patrimonio*0.99, y=media_vida*1.01, text="Alto Risco à Vida", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color="orange", size=12))
    fig_matrix.add_annotation(x=media_patrimonio*1.01, y=media_vida*0.99, text="Alto Risco Patrimonial", showarrow=False, xanchor='left', yanchor='top', font=dict(color="orange", size=12))
    fig_matrix.add_annotation(x=media_patrimonio*0.99, y=media_vida*0.99, text="Baixo Risco (Ambos)", showarrow=False, xanchor='right', yanchor='top', font=dict(color="green", size=12))

    # Removemos o plotly_events e apenas exibimos o gráfico
    st.plotly_chart(fig_matrix, use_container_width=True)


# --- ABA 4: Detalhe por Cluster (NOVA LÓGICA) ---
with tab4:
    st.title("Análise Detalhada por Cluster")
    
    # 1. O Menu Dropdown
    # Usamos o df_perfis original (sem filtro de sidebar) para popular o menu
    all_profiles_list = sorted(df_perfis['perfil_risco'].unique())
    selected_profile = st.selectbox(
        "Selecione um Perfil de Risco para analisar:",
        options=all_profiles_list
    )
    
    if selected_profile:
        # 2. Buscar os dados
        # Pega os dados de perfil (médias dos KPIs)
        profile_data = df_perfis[df_perfis['perfil_risco'] == selected_profile].iloc[0]
        
        # Pega os dados temporais (para histórico e dados das AISPs)
        cluster_id = profile_data['cluster_id']
        temporal_data_cluster = df_temporal[df_temporal['cluster_id'] == cluster_id]
        
        # 3. Storytelling
        st.subheader(f"Storytelling: O Perfil do '{selected_profile}'")
        
        # Recalcula KPIs agregados para o storytelling (usando dados de todos os anos)
        soma_recup = temporal_data_cluster['recuperacao_veiculos'].sum()
        soma_roubo_v = temporal_data_cluster['roubo_veiculo'].sum()
        kpi_recup = (soma_recup / soma_roubo_v) if soma_roubo_v > 0 else 0
        
        kpi_fuzil = profile_data['armas_arma_fogo_fuzil']
        kpi_confronto = profile_data['Proporcao_Confronto']
        n_aisps = profile_data['n_de_aisps']

        st.markdown(f"""
        O **{selected_profile}** é um cluster composto por **{n_aisps} AISPs**. 
        Este perfil pode ser compreendido através dos seus principais KPIs:

        * **Nível de Ameaça:** A média de fuzis apreendidos (KPI 2) é de **{kpi_fuzil:.2f}**. 
            Este é um indicador chave do nível de armamento das organizações criminosas na área.
        * **Perfil de Confronto:** **{kpi_confronto:.1f}%** de toda a letalidade violenta (KPI 6) neste 
            cluster é resultado direto de intervenção policial, indicando o nível de conflito.
        * **Eficácia da Resposta:** A taxa de recuperação de veículos (KPI 1) é de **{kpi_recup:.1%}**. 
            Isso mede a eficiência da resposta policial ao roubo de veículos.
        """)
        
        st.divider()

        # 4. Histórico
        st.subheader(f"Histórico: Evolução do Roubo de Rua ({selected_profile})")
        # Usa os dados temporais do cluster (sem filtro de ano da sidebar)
        df_evolucao_cluster = temporal_data_cluster.groupby(['ano', 'mes'])['roubo_rua'].sum().reset_index()
        df_evolucao_cluster['data'] = pd.to_datetime(df_evolucao_cluster[['ano', 'mes']].assign(day=1).rename(columns={'ano': 'year', 'mes': 'month'}))
        
        fig_linha_cluster = px.line(
            df_evolucao_cluster, x='data', y='roubo_rua',
            title=f"Evolução do Total de Roubos de Rua ({selected_profile})",
            labels={'data': 'Data', 'roubo_rua': 'Total de Roubos de Rua'}
        )
        st.plotly_chart(fig_linha_cluster, use_container_width=True)

        st.divider()

        # 5. Dados (AISPs)
        st.subheader(f"Dados: AISPs pertencentes ao {selected_profile}")
        st.markdown(f"A tabela abaixo mostra a média dos indicadores para cada AISP deste cluster, *considerando os anos filtrados na barra lateral* ({ano_filtro[0]} a {ano_filtro[1]}).")

        # Filtra os dados temporais do cluster usando o FILTRO DE ANO da sidebar
        df_aisp_details = temporal_data_cluster[
            (temporal_data_cluster['ano'] >= ano_filtro[0]) & 
            (temporal_data_cluster['ano'] <= ano_filtro[1])
        ]
        
        cols_para_agregar = ['letalidade_violenta', 'roubo_rua', 'roubo_veiculo', 'total_furtos', 'total_roubos', 'apreensao_drogas', 'armas_arma_fogo_fuzil']
        cols_existentes = [col for col in cols_para_agregar if col in df_aisp_details.columns]
        df_aisp_agg = df_aisp_details.groupby("aisp")[cols_existentes].mean().reset_index()
        
        aisp_list = sorted(df_aisp_agg['aisp'].unique())
        st.markdown(f"**AISPs (Bairros/Áreas) neste cluster:** `{', '.join(map(str, aisp_list))}`")
        
        st.dataframe(df_aisp_agg.style.format("{:.2f}"), use_container_width=True)