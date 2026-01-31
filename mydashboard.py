import streamlit as st
from views import Overview
from views import US_stocks
from views import Funds
from views import AI_analyze

st.set_page_config(
    page_title="Wealth Command Center",
    page_icon="💰",
    layout="wide"
)


st.title("🏥 Wealth Command Center")

tab1, tab2, tab3,tab4 = st.tabs(["Home","US Stocks", "Funds","🤖 AI Advisor"])

with tab1:
    Overview.show()
with tab2:
    try:
        US_stocks.show() 
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหน้าหุ้น: {e}")
        st.info("💡 อย่าลืมแก้ไฟล์ us_stock.py ให้มี def show(): ครอบโค้ดไว้นะครับ")

with tab3:
    Funds.show()

with tab4:
    AI_analyze.show()