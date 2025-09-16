import streamlit as st
import pandas as pd
import altair as alt
import json
from itertools import chain

# ============================================================
# WORKING WITH DATA
# ============================================================

# --- Loading the dataset ---
DATASET_FILE = "with_human_verification.json"

try:
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    st.error(f"Error opening {DATASET_FILE}: {e}")
    st.stop()

if not isinstance(data, list):
    st.error("Unexpected JSON format: expected a list of objects (list of examples).")
    st.stop()

# Create main DataFrame (for hops charts, etc.)
df = pd.DataFrame(data)

# ============================================================
# DASHBOARD VISUALIZATION
# ============================================================

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="MoreHopQA - Visualizations")

# --- Title ---
st.title("MoreHopQA Dataset Visualizations")

# --- Explanatory Text ---
st.markdown("""
This notebook loads the **MoreHopQA** dataset and presents some exploratory visualizations using **Altair**.

The dataset contains complex questions that require multiple reasoning steps.  
Columns record everything from the original question and its answer to the decomposition into subquestions, the supporting paragraphs used, and metadata about reasoning type, decomposition patterns, and simplifications of the question.

---

### Summary of MoreHopQA columns
- **question** → Original question in the dataset.  
- **answer** → Expected final answer for the question.  
- **answer_type** → Type of the answer (e.g., entity, number, yes/no).  
- **reasoning_type** → Type of reasoning required (e.g., *Symbolic, Arithmetic, Commonsense*).  
- **decomp_len** → Number of hops (subquestions) used in the question decomposition.  
- **question_decomposition** → List of subquestions/hops, each with supporting information and links.  
- **paragraph_support_title** *(inside decomposition)* → Paragraph(s) used to answer that subquestion.  
- **pattern** → Global logical structure of the question (e.g., *sequential, intersection, comparison*).  
- **subquestion_pattern** → Logical structure of each subquestion in the decomposition (e.g., *lookup, bridge*).  
- **cutted_question** → Simplified/reduced version of the original question.  
- **ques_on_last_hop** → Flag indicating if the final answer depends only on the last hop.  
- **id** → Unique identifier of the question in the dataset.  
- **supporting_facts** → List of facts (titles and sentences) justifying the answer.  
- **num_paragraphs** *(derived)* → Number of supporting paragraphs (created during preprocessing).  

---
""")

st.markdown("""
Example of a dataset record:
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
# ROW 1: Hops Chart and Heatmap
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("CHART: Number of hops")

    if "no_of_hops" not in df.columns and "num_hops" in df.columns:
        df["no_of_hops"] = df["num_hops"]

    if "no_of_hops" not in df.columns:
        st.error("Could not find/derive 'no_of_hops' column in the dataset.")
    else:
        if "answer_type" in df.columns:
            df_plot = df[["no_of_hops", "answer_type"]].copy()
        else:
            df_plot = df[["no_of_hops"]].copy()

        base = alt.Chart(df_plot).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        if "answer_type" in df_plot.columns:
            chart_hops = base.encode(
                x=alt.X('no_of_hops:O', title='Number of hops'),
                y=alt.Y('count()', title="Number of answers"),
                color=alt.Color('answer_type:N', legend=alt.Legend(title="Answer Types")),
                tooltip=['no_of_hops', 'answer_type']
            ).properties(title='Distribution of number of hops', height=500).interactive()
        else:
            chart_hops = base.encode(
                x=alt.X('no_of_hops:O', title='Number of hops'),
                y=alt.Y('count()', title="Number of answers"),
                tooltip=['no_of_hops']
            ).properties(title='Distribution of number of hops', height=500).interactive()

        st.altair_chart(chart_hops, use_container_width=True)

with col2:
    st.subheader("CHART: Heatmap - Answer Type x Reasoning Type")

    if "reasoning_type" not in df.columns or "answer_type" not in df.columns:
        st.error("Required columns ('reasoning_type', 'answer_type') not found in the dataset.")
    else:
        heatmap_data = df.groupby(['reasoning_type', 'answer_type']).size().reset_index(name='count')

        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('answer_type:N', title='Answer Type'),
            y=alt.Y('reasoning_type:N', title='Reasoning Type'),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='greens'), title='Number of Questions'),
            tooltip=['reasoning_type', 'answer_type', 'count']
        ).properties(
            title='Heatmap: Answer Type x Reasoning Type',
            height=500
        )

        st.altair_chart(heatmap, use_container_width=True)

# ============================================================
# ROW 2: Chart - Most used supporting paragraphs
# ============================================================

flattened_supports = list(chain.from_iterable(
    [title for title, _ in item.get("context", [])]
    for item in data
))

# Count frequency
support_counts = (
    pd.Series(flattened_supports)
    .value_counts()
    .reset_index()
    .rename(columns={"index": "paragraphs", 0: "count"})
)

chart_support = alt.Chart(support_counts).mark_circle().encode(
    x=alt.X('paragraphs:N', title='Supporting Paragraph', axis=alt.Axis(labelAngle=-45, labelLimit=300)),
    y=alt.Y('count:Q', title='Frequency'),
    size='count:Q',
    tooltip=['paragraphs', 'count']
).properties(title='Most used supporting paragraphs')

chart_support
