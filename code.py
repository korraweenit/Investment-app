import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Med-Tech Analyst", layout="wide")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    df=pd.read_csv(uploaded_file)
    st.dataframe(df.head(10))

    if 'Date' in df.columns:
        df['Date']=pd.to_datetime(df['Date'])
        df = df.set_index('Date')

    st.subheader("Line chart")
    value= st.selectbox("select value",df.columns)
    chart_df=df[value]
    st.line_chart(chart_df)

    st.subheader("Interactive Histogram")
    fig, ax = plt.subplots()
    value2= st.selectbox("select hist_value",df.columns)
    Histogram_df=df[value2]

    bins_v=st.slider("bins",5,100,30)

    ax.hist(Histogram_df, bins=bins_v, alpha=0.6, label=value2, color='green')
    st.pyplot(fig)
else:
    st.warning('Please upload data', icon="⚠️")