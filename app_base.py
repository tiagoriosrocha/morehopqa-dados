import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard de Exemplo com Altair")

# --- Título ---
st.title("Dashboard com Gráficos Altair e Dados Fixos")
st.markdown("Este é um exemplo de como exibir múltiplos gráficos com a biblioteca Altair no Streamlit.")

# --- DADOS FIXOS (HARDCODED) ---

# Dados para o Gráfico de Barras (Vendas por Categoria)
data_barras = pd.DataFrame({
    'Categoria': ['Eletrônicos', 'Móveis', 'Roupas', 'Livros', 'Brinquedos'],
    'Vendas (em milhões)': [120, 85, 95, 60, 45]
})

# Dados para o Gráfico de Linha (Crescimento de Usuários ao longo do tempo)
data_linha = pd.DataFrame({
    'Mês': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01']),
    'Novos Usuários': [1500, 1800, 2200, 2100, 2500, 3100]
})

# Dados para o Gráfico de Dispersão (Relação entre Preço e Avaliação de Produtos)
np.random.seed(42) # Para resultados reproduzíveis
data_dispersao = pd.DataFrame({
    'Preço (R$)': np.random.uniform(50, 500, 100),
    'Avaliação (0-5)': np.random.uniform(2.5, 5, 100)
})
# Adiciona uma correlação artificial
data_dispersao['Avaliação (0-5)'] = data_dispersao['Avaliação (0-5)'] - (data_dispersao['Preço (R$)'] / 500)


# --- CRIAÇÃO DOS GRÁFICOS ---

# Gráfico 1: Barras
grafico_barras = alt.Chart(data_barras).mark_bar(
    cornerRadiusTopLeft=5,
    cornerRadiusTopRight=5,
    color="#4c78a8"
).encode(
    x=alt.X('Categoria:N', sort='-y', title='Categoria do Produto'),
    y=alt.Y('Vendas (em milhões):Q', title='Vendas (em Milhões de R$)'),
    tooltip=['Categoria', 'Vendas (em milhões)']
).properties(
    title='Volume de Vendas por Categoria'
).interactive()

# Gráfico 2: Linha
grafico_linha = alt.Chart(data_linha).mark_line(
    point=True,
    strokeWidth=3,
    color="#f58518"
).encode(
    x=alt.X('Mês:T', title='Mês'),
    y=alt.Y('Novos Usuários:Q', title='Novos Usuários Registrados'),
    tooltip=['Mês', 'Novos Usuários']
).properties(
    title='Crescimento Mensal de Novos Usuários'
).interactive()

# Gráfico 3: Dispersão (Scatter Plot)
grafico_dispersao = alt.Chart(data_dispersao).mark_circle(
    size=60,
    opacity=0.7,
    color="#e45756"
).encode(
    x=alt.X('Preço (R$):Q', scale=alt.Scale(zero=False)),
    y=alt.Y('Avaliação (0-5):Q', scale=alt.Scale(zero=False)),
    tooltip=['Preço (R$)', 'Avaliação (0-5)']
).properties(
    title='Relação entre Preço e Avaliação do Produto'
).interactive()


# --- EXIBIÇÃO DOS GRÁFICOS NO DASHBOARD ---

st.header("Visualizações de Dados")

# Organiza os gráficos em colunas
col1, col2 = st.columns(2)

with col1:
    st.altair_chart(grafico_barras, use_container_width=True)
    st.altair_chart(grafico_dispersao, use_container_width=True)

with col2:
    st.altair_chart(grafico_linha, use_container_width=True)


