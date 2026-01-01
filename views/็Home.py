import streamlit as st
import pandas as pd

def main():
    st.header("🏠 Home Overview")
    
    # --- 1. Emergency Fund (ส่วนบนสุด) ---
    # ใช้ st.container เพื่อจัดกลุ่มให้ดูเป็นสัดส่วน
    with st.container(border=True):
        col_em1, col_em2 = st.columns([3, 1])
        with col_em1:
            st.subheader("🛡️ Emergency Fund")
            st.caption("เงินสำรองฉุกเฉิน (เป้าหมาย: 50,000 บาท)")
        with col_em2:
            # แสดงตัวเลขโดดๆ ชัดๆ
            st.metric(label="Current Amount", value="15,100 ฿", delta="30% of Goal")
        
        # หลอด Progress Bar แบบ Native (ใช้ง่ายมาก)
        st.progress(0.30, text="ความปลอดภัยทางการเงิน: Safe Level 1")

    st.markdown("---")

    # --- 2. Key Metrics (สรุปภาพรวมพอร์ต) ---
    # ข้อมูลตัวอย่าง (เดี๋ยวเราค่อยดึงจาก Google Sheet มาใส่แทน)
    total_asset = 125339
    total_invested = 81273
    total_profit = total_asset - total_invested
    profit_percent = (total_profit / total_invested) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("💎 Net Worth (ทรัพย์สินรวม)", f"฿ {total_asset:,.0f}")
    c2.metric("💸 Invested (ต้นทุน)", f"฿ {total_invested:,.0f}")
    c3.metric("📈 Profit/Loss (กำไร)", f"฿ {total_profit:,.0f}", f"{profit_percent:.2f}%")

    st.markdown("---")

    # --- 3. Asset Breakdown & Graph (แบ่งซ้ายขวา) ---
    col_left, col_right = st.columns([1, 2]) # แบ่งสัดส่วน ซ้าย 1 : ขวา 2

    with col_left:
        st.subheader("📋 Asset Breakdown")
        # สร้างข้อมูลจำลองตารางสินทรัพย์
        asset_data = pd.DataFrame({
            "Asset": ["US Stock", "Mutual Fund", "Savings", "Gold", "Thai Stock", "Bitcoin"],
            "Value": [33425, 28252, 27121, 5333, 1602, 14505],
            "Type": ["Invest", "Invest", "Cash", "Invest", "Invest", "Speculate"]
        })
        # แสดงเป็นตารางธรรมดา แต่เปิดใช้ Column Configuration ให้สวย
        st.dataframe(
            asset_data,
            column_config={
                "Value": st.column_config.NumberColumn("มูลค่า (บาท)", format="฿ %d"),
                "Asset": "สินทรัพย์",
            },
            hide_index=True,
            use_container_width=True
        )

    with col_right:
        st.subheader("📈 Wealth Evolution")
        # สร้างข้อมูลจำลองกราฟ (Wealth vs Cost)
        # (อันนี้ต้องมี Sheet เก็บ History ในอนาคตครับ ตอนนี้ Mock ไปก่อน)
        chart_data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Market Value": [80000, 85000, 82000, 95000, 105000, 125339],
            "Cost":         [75000, 78000, 80000, 82000, 85000, 81273]
        })
        
        # วาดกราฟเส้น Area Chart (Native Streamlit)
        st.area_chart(
            chart_data.set_index("Month"),
            color=["#2E8B57", "#A9A9A9"] # สีเขียว (Value), สีเทา (Cost)
        )
        st.caption("หมายเหตุ: เส้นสีเขียวคือมูลค่าพอร์ตปัจจุบัน, สีเทาคือต้นทุน")