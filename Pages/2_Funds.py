# pages/2_🇹🇭_Mutual_Funds.py
import streamlit as st
import utils # เรียกใช้สมองกลาง

st.set_page_config(page_title="Mutual Funds", layout="wide")

st.title("🇹🇭 Thai Mutual Funds")
st.info("🚧 Work in Progress: เตรียมพบกับระบบติดตามกองทุนเร็วๆ นี้")

# ในอนาคตคุณหมอจะเขียน load_data ของกองทุนที่นี่
# และเรียก utils.update_portfolio_hx(..., hx_worksheet='Fund_Hx', benchmark_ticker='^SET.BK')