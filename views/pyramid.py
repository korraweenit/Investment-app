import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
@st.cache_data(ttl=600)
def load_pyramid_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="rebalance", skiprows=1)
    df = df.iloc[:4, 11:19]
    df.columns = ['Pyramid', 'Asset', 'Invest', 'Value', 'GainLoss', 'Portion (%)', 'Target(%)']
    return df

# -------------------------------------------------------
# 🎨 PYRAMID CONFIGURATION
# -------------------------------------------------------
# กำหนดสีให้ตรงกับ Theme (High-risk=แดง, Foundation=เขียว)
PYRAMID_THEME = {
    "High-risk":  {"color": "#e03131", "width": "25%"},  # แดงเข้ม (ยอด)
    "Growth":     {"color": "#fd7e14", "width": "50%"},  # ส้ม
    "Core":       {"color": "#fcc419", "width": "75%"},  # เหลืองทอง
    "Foundation": {"color": "#37b24d", "width": "100%"}  # เขียว (ฐาน)
}

# -------------------------------------------------------
# 🏗️ RENDER FUNCTION
# -------------------------------------------------------
def render_pyramid_from_db(df):
    layer_order = ["High-risk", "Growth", "Core", "Foundation"]
    
    # ⚠️ สังเกต: ผมขยับ <style> และ <div> ให้ชิดซ้าย ไม่ให้มีเว้นวรรคข้างหน้า
    html_content = """
<style>
    .pyramid-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin: 20px 0;
        font-family: 'Segoe UI', sans-serif;
    }
    .p-layer {
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        margin-bottom: 4px;
        position: relative;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        min-height: 65px;
    }
    .p-layer:hover { transform: scale(1.02); z-index: 10; }
    .p-content { padding: 5px; line-height: 1.2; }
    .p-title { font-weight: 800; font-size: 15px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }
    .p-assets { font-size: 12px; font-weight: 500; opacity: 0.95; margin-top: 4px; word-wrap: break-word;}
    .stat-box {
        position: absolute;
        font-size: 13px; font-weight: 700;
        white-space: nowrap;
        color: #495057;
        background: rgba(255,255,255,0.8);
        padding: 2px 8px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stat-left { left: -100px; text-align: right; width: 90px; }
    .stat-right { right: -100px; text-align: left; width: 90px; }
    .label-sub { font-size: 10px; color: #868e96; font-weight: normal; }
</style>
<div class="pyramid-container">
"""
    
    for i, layer_name in enumerate(layer_order):
        # ... (ส่วนดึงข้อมูลเหมือนเดิม) ...
        # (Copy Logic เดิมมาใส่ตรงนี้ได้เลยครับ หรือใช้ตัวเต็มข้างล่าง)
        
        # --- Logic ดึงข้อมูล (ผมใส่ไว้ให้ครบเผื่อก๊อปปี้ทีเดียว) ---
        row = df[df['Pyramid'].astype(str).str.contains(layer_name, case=False, na=False)]
        if not row.empty:
            r = row.iloc[0]
            assets_str = str(r['Asset']) if pd.notnull(r['Asset']) else "-"
            if len(assets_str) > 40: assets_str = assets_str[:40] + "..."
            actual_pct = r['Portion (%)'] if pd.notnull(r['Portion (%)']) else 0
            target_pct = r['Target(%)'] if pd.notnull(r['Target(%)']) else 0
            if actual_pct < 1.05: actual_pct *= 100
            if target_pct < 1.05: target_pct *= 100
        else:
            assets_str = "No Assets"; actual_pct = 0; target_pct = 0

        theme = PYRAMID_THEME.get(layer_name, {"color": "#888", "width": "50%"})
        bg_color = theme["color"]
        width = theme["width"]
        border_style = "border-radius: 12px 12px 4px 4px;" if i==0 else "border-radius: 4px;"
        if i == 3: border_style = "border-radius: 4px 4px 12px 12px;"

        # ⚠️ แก้ตรงนี้สำคัญ: ชิดซ้ายเหมือนกัน
        html_content += f"""
<div class="p-layer" style="width: {width}; background: {bg_color}; {border_style}">
    <div class="stat-box stat-left">
        {actual_pct:.1f}%
        <div class="label-sub">Actual</div>
    </div>
    <div class="p-content">
        <div class="p-title">{layer_name}</div>
        <div class="p-assets">{assets_str}</div>
    </div>
    <div class="stat-box stat-right">
        {target_pct:.0f}%
        <div class="label-sub">Target</div>
    </div>
</div>
"""
        
    html_content += "</div>"
    return html_content

# -------------------------------------------------------
# 🚀 เรียกใช้งาน (ตัวอย่าง)
# -------------------------------------------------------
allocation_df=load_pyramid_data()

def show_pyramid():
    st.markdown("### 🏛️ Portfolio Pyramid Structure")
    # เรียกฟังก์ชัน Render
    html = render_pyramid_from_db(allocation_df)
    st.markdown(html, unsafe_allow_html=True)
    
    # (Optional) แสดงตารางดิบๆ ด้านล่างเผื่อเช็คยอด
    with st.expander("🔍 ดูข้อมูลตารางละเอียด"):
        st.dataframe(
            allocation_df,
            column_config={
                "Portion (%)": st.column_config.NumberColumn(format="%.2f%%"),
                "Target(%)": st.column_config.NumberColumn(format="%.0f%%"),
                "Value (฿)": st.column_config.NumberColumn(format="฿ %.0f")
            },
            hide_index=True,
            use_container_width=True
        )