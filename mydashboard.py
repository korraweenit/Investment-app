import streamlit as st
# Import ไฟล์จากห้อง views มาใช้งาน
from views import US_stocks
from views import Funds

st.set_page_config(
    page_title="Wealth Command Center",
    page_icon="💰",
    layout="wide"
)

# ส่วนหัวของ Dashboard
st.title("🏥 Dr. Bew's Wealth Command Center")

# --- สร้าง Tabs (พระเอกของเรา) ---
tab1, tab2, tab3 = st.tabs(["Home","US Stocks", "Funds"])

with tab1:
    st.title("Home Dashboard")
with tab2:
    try:
        US_stocks.main() 
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหน้าหุ้น: {e}")
        st.info("💡 อย่าลืมแก้ไฟล์ us_stock.py ให้มี def show(): ครอบโค้ดไว้นะครับ")

with tab3:
    try:
        Funds.show()
    except Exception as e:
        st.warning("หน้านี้กำลังพัฒนาครับ (Waiting for Thai Funds code)")