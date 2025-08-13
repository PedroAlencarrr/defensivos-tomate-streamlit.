import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Configuração do Banco de Dados ---
# O caminho do DB precisa ser absoluto para o Streamlit Cloud
# Como o database.db estará na pasta src, ajustamos o caminho
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'src', 'database.db')

# --- Funções de Carregamento de Dados ---
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

# --- Layout do Streamlit ---
st.set_page_config(
    page_title="Consulta de Defensivos para Tomate Envarado",
    page_icon="🍅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Consulta de Defensivos para Tomate Envarado")

# Carregar dados
df_produtos = load_data()

# --- Abas ---
tab_geral, tab_mosca_branca = st.tabs(["Geral", "Mosca Branca"])

with tab_geral:
    st.header("Informações Gerais")

    # Métricas
    total_produtos = len(df_produtos)
    total_alvos = df_produtos["Alvo"].nunique()
    total_grupos_quimicos = df_produtos["Grupo Químico"].nunique()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Produtos Registrados", value=total_produtos)
    with col2:
        st.metric(label="Pragas e Doenças", value=total_alvos)
    with col3:
        st.metric(label="Grupos Químicos", value=total_grupos_quimicos)

    st.markdown("--- ")

    # Filtros e Busca
    search_query = st.text_input("Buscar por nome, ingrediente, alvo...", "")

    filtered_df = df_produtos.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Nome Comercial"].str.contains(search_query, case=False, na=False) |
            filtered_df["Ingrediente Ativo"].str.contains(search_query, case=False, na=False) |
            filtered_df["Alvo"].str.contains(search_query, case=False, na=False)
        ]
    
    st.subheader("Resultados da Busca")
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("Nenhum produto encontrado com os filtros aplicados.")

with tab_mosca_branca:
    st.header("Produtos Específicos para Mosca Branca")

    df_mosca_branca = df_produtos[df_produtos["Mosca Branca"] == 1]

    total_mb_produtos = len(df_mosca_branca)
    total_mb_ingredientes = df_mosca_branca["Ingrediente Ativo"].nunique()

    col1_mb, col2_mb = st.columns(2)
    with col1_mb:
        st.metric(label="Produtos para Mosca Branca", value=total_mb_produtos)
    with col2_mb:
        st.metric(label="Ingredientes Ativos Únicos (MB)", value=total_mb_ingredientes)

    st.markdown("--- ")

    if not df_mosca_branca.empty:
        st.dataframe(df_mosca_branca, use_container_width=True)
    else:
        st.info("Nenhum produto específico para Mosca Branca encontrado.")