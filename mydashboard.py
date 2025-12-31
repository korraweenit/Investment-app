# Home.py
import streamlit as st

st.set_page_config(
    page_title="Wealth Command Center",
    page_icon="💰",
    layout="wide"
)

st.title("🏥 Dr. Bew's Wealth Command Center")
st.markdown("### Welcome back, Doctor!")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.success("🇺🇸 **US Stocks**\n\nติดตามพอร์ตหุ้นอเมริกา เปรียบเทียบ SP500")
    st.page_link("pages/1_US_stocks.py", label="Go to US Stocks", icon="🇺🇸")

with col2:
    st.info("🇹🇭 **Mutual Funds**\n\nติดตามกองทุนรวมไทย (Coming Soon)")
    st.page_link("pages/2_Funds.py", label="Go to Funds", icon="🇹🇭")