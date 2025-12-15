import pandas as pd
import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bi_narrator.chain import chain
from bi_narrator.system_prompt import system_prompt

# Setting up the page title
st.set_page_config(page_title="BI Narrator", layout="wide")

st.title("📊 BI Narrator")

uploaded = st.file_uploader("Upload CSV file", type=["csv"])

# processing the file to generate the narrative
if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.error("No numeric columns found in the dataset.")
        st.stop()

    date_col = st.selectbox("Select Date Column", columns)
    metric_col = st.selectbox("Select Metric Column (numeric only)", numeric_cols)
    category_col = st.selectbox("Select Category Column", ["None"] + columns)

    audience = st.text_input("Audience", "Executive leadership")
    tone= st.text_input("Tone", "Insightful & advisory")

    if st.button("Generate Narrative"):
        map_input = {
            "prompt_input": {
                "audience": audience,
                "tone": tone,
                "system_prompt": system_prompt
            },
            "data": df,
            "date_col": date_col,
            "metric_col": metric_col,
            "category_col": None if category_col == "None" else category_col
        }

        with st.spinner("Running analysis and generating narrative..."):
            try:
                output_text = chain.invoke(map_input)
            
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

        st.subheader("📝 BI Narrative")
        st.write(output_text)