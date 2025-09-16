import streamlit as st
import pandas as pd
import altair as alt
import json
from itertools import chain

# ============================================================
# TRABALHANDO NOS DADOS
# ============================================================

# --- Carregando o dataset ---
DATASET_FILE = "with_human_verification.json"

try:
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    st.error(f"Erro ao abrir {DATASET_FILE}: {e}")
    st.stop()

if not isinstance(data, list):
    st.error("Formato do JSON inesperado: esperava-se uma lista de objetos (uma lista de exemplos).")
    st.stop()

# Monta DataFrame principal (para gráficos de hops, etc.)
df = pd.DataFrame(data)






# ============================================================
# GERANDO A VISUALIZAÇÃO DO DASHBOARD
# ============================================================

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="MoreHopQA - Visualizações")

# --- Título ---
st.title("Visualizações do Dataset MoreHopQA")

# --- Texto explicativo ---
st.markdown("""
Este notebook carrega o dataset **MoreHopQA** e apresenta algumas visualizações exploratórias usando **Altair**.

O dataset traz perguntas complexas que exigem múltiplos passos de raciocínio.  
As colunas registram desde a pergunta original e sua resposta, até a decomposição em subperguntas, os parágrafos de suporte utilizados, e metadados sobre o tipo de raciocínio, padrões de decomposição e simplificações da pergunta.

---

### Resumo das colunas do MoreHopQA
- **question** → Pergunta original feita no dataset.  
- **answer** → Resposta final esperada para a pergunta.  
- **answer_type** → Tipo da resposta (ex.: entidade, número, sim/não).  
- **reasoning_type** → Tipo de raciocínio necessário (ex.: *Symbolic, Arithmetic, Commonsense*).  
- **decomp_len** → Quantidade de hops (subperguntas) usados na decomposição da pergunta.  
- **question_decomposition** → Lista com as subperguntas/hops, cada uma com informações de suporte e ligação.  
- **paragraph_support_title** *(dentro da decomposição)* → Parágrafo(s) de suporte usados para responder àquela subpergunta.  
- **pattern** → Estrutura lógica global da pergunta (ex.: *sequential, intersection, comparison*).  
- **subquestion_pattern** → Estrutura lógica de cada subpergunta dentro da decomposição (ex.: *lookup, bridge*).  
- **cutted_question** → Versão simplificada/reduzida da pergunta original, com partes irrelevantes cortadas.  
- **ques_on_last_hop** → Flag indicando se a resposta final depende apenas do último hop da decomposição.  
- **id** → Identificador único da pergunta no dataset.  
- **supporting_facts** → Lista de fatos (títulos e frases) que justificam a resposta.  
- **num_paragraphs** *(derivada)* → Quantidade de parágrafos usados como suporte (coluna criada no pré-processamento).  
            
---

""")

st.markdown("""
Exemplo de um registro do dataset:
- **_id**: 5ae5072e55429960a22e0246_13
- **question**: How many repeated letters are there in the first name of the current drummer of the band who did the song "What Lovers Do"?
- **answer**: 1
- **previous_question**: Who is the current drummer of the band who did the song "What Lovers Do"?
- **previous_answer**: Matt Flynn
- **question_decomposition**: [{'sub_id': '1', 'question': 'Which band did the song "What Lovers Do"?', 'answer': 'Maroon 5', 'paragraph_support_title': 'What Lovers Do'}, {'sub_id': '2', 'question': 'Who is the current drummer of Maroon 5?', 'answer': 'Matt Flynn', 'paragraph_support_title': 'Maroon 5'}, {'sub_id': '3', 'question': 'How many repeated letters are there in the first name of Matt Flynn?', 'answer': '1', 'paragraph_support_title': '', 'details': [{'sub_id': '3_1', 'question': 'What is the first name of Matt Flynn?', 'answer': 'Matt', 'paragraph_support_title': ''}, {'sub_id': '3_2', 'question': 'How many repeated letters are there in Matt?', 'answer': '1', 'paragraph_support_title': ''}]}]
- **context**: [['Maroon 5', ['Maroon 5 is an American pop rock band that originated in Los Angeles, California.', ' It currently consists of lead vocalist Adam Levine, keyboardist and rhythm guitarist Jesse Carmichael, bassist Mickey Madden, lead guitarist James Valentine, drummer Matt Flynn and keyboardist PJ Morton.']], ['What Lovers Do', ['"What Lovers Do" is a song by American pop rock band Maroon 5 featuring American R&B singer Sza.', " It was released on August 30, 2017, as the third single from the band's upcoming sixth studio album (2017).", ' The song contains an interpolation of the 2016 song "Sexual" by Neiked featuring Dyo, therefore Victor Rådström, Dyo and Elina Stridh are credited as songwriters.']]]
- **answer_type**: number
- **previous_answer_type**: person
- **no_of_hops**: 2
- **reasoning_type**: Commonsense, Arithmetic
- **pattern**: How many repeated letters are there in the first name of #Name?
- **subquestion_patterns**: ['What is the first name of #Name?', 'How many repeated letters are there in #Ans1?']
- **cutted_question**: the current drummer of the band who did the song "What Lovers Do"
- **ques_on_last_hop**: How many repeated letters are there in the first name of the current drummer of Maroon 5?
            
---

""")




# ============================================================
# LINHA 1: Gráfico - Hops e Gráfico  - Heatmap
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("GRÁFICO: Número de hops")

    if "no_of_hops" not in df.columns and "num_hops" in df.columns:
        df["no_of_hops"] = df["num_hops"]

    if "no_of_hops" not in df.columns:
        st.error("Não foi possível encontrar/derivar a coluna 'no_of_hops' no dataset.")
    else:
        if "answer_type" in df.columns:
            df_plot = df[["no_of_hops", "answer_type"]].copy()
        else:
            df_plot = df[["no_of_hops"]].copy()

        base = alt.Chart(df_plot).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        if "answer_type" in df_plot.columns:
            chart_hops = base.encode(
                x=alt.X('no_of_hops:O', title='Número de hops'),
                y=alt.Y('count()', title="Quantidade de respostas"),
                color=alt.Color('answer_type:N', legend=alt.Legend(title="Tipos de Respostas")),
                tooltip=['no_of_hops', 'answer_type']
            ).properties(title='Distribuição do número de hops', height=500).interactive()
        else:
            chart_hops = base.encode(
                x=alt.X('no_of_hops:O', title='Número de hops'),
                y=alt.Y('count()', title="Quantidade de respostas"),
                tooltip=['no_of_hops']
            ).properties(title='Distribuição do número de hops', height=500).interactive()

        st.altair_chart(chart_hops, use_container_width=True)

with col2:
    st.subheader("GRÁFICO: Heatmap - Tipo de Resposta x Tipo de Raciocínio")

    if "reasoning_type" not in df.columns or "answer_type" not in df.columns:
        st.error("As colunas necessárias ('reasoning_type', 'answer_type') não foram encontradas no dataset.")
    else:
        heatmap_data = df.groupby(['reasoning_type', 'answer_type']).size().reset_index(name='count')

        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('answer_type:N', title='Tipo de Resposta'),
            y=alt.Y('reasoning_type:N', title='Tipo de Raciocínio'),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='greens'), title='Número de Perguntas'),
            tooltip=['reasoning_type', 'answer_type', 'count']
        ).properties(
            title='Heatmap: Tipo de Resposta x Tipo de Raciocínio',
            height=500
        )

        st.altair_chart(heatmap, use_container_width=True)






# ============================================================
# LINHA 2: Gráfico - Parágrafos de suporte mais usados
# ============================================================

flattened_supports = list(chain.from_iterable(
    [title for title, _ in item.get("context", [])]
    for item in data
))

# Conta frequência
support_counts = (
    pd.Series(flattened_supports)
    .value_counts()
    .reset_index()
    .rename(columns={"index": "paragraphs", 0: "count"})
)

chart_support = alt.Chart(support_counts).mark_circle().encode(
    x=alt.X('paragraphs:N', title='Parágrafo de suporte', axis=alt.Axis(labelAngle=-45, labelLimit=300)),
    y=alt.Y('count:Q', title='Frequência'),
    size='count:Q',
    tooltip=['paragraphs', 'count']
).properties(title='Parágrafos mais usados como suporte')

chart_support