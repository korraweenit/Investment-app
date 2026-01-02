import streamlit as st
import pandas as pd
import altair as alt
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------
# 1. Load & Clean Data
# -------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="rebalance", skiprows=1)
    df = df.iloc[:10, 6:11]
    df.columns = ['AssetName', 'Invest', 'Value', 'GainLoss_Text', 'Portion']
    
    cols_to_num = ['Invest', 'Value']
    for col in cols_to_num:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
    return df

# -------------------------------------------------------
# 2. Main Show Function
# -------------------------------------------------------
def show():
    # --- CSS Styling ---
    st.markdown("""
        <style>
        .stApp { background-color: #f4f6f9; }
        
        .metric-card {
            background-color: white; border-radius: 16px; padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e0e0e0;
        }
        .metric-label { font-size: 14px; font-weight: 600; color: #666; text-transform: uppercase; }
        .metric-value { font-size: 30px; font-weight: 800; color: #1a5d3a; font-family: 'Segoe UI', sans-serif; }
        .metric-delta { font-size: 14px; font-weight: 700; margin-top: 5px; }

        .asset-item {
            background-color: white; padding: 15px 20px; border-radius: 16px; margin-bottom: 12px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-left: 6px solid #1a5d3a;
            transition: transform 0.2s;
        }
        .asset-item:hover { transform: scale(1.02); }
        
        .asset-name { font-weight: 800; font-size: 16px; color: #2c3e50; }
        .asset-badge {
            background-color: #e8f5e9; color: #1b5e20; padding: 2px 8px; border-radius: 10px;
            font-size: 12px; font-weight: 700; display: inline-block; margin-top: 4px;
        }
        .asset-val { font-weight: 800; font-size: 18px; color: #333; text-align: right; }
        
        .gain-text { font-size: 13px; font-weight: 700; color: #28a745; text-align: right; }
        .loss-text { font-size: 13px; font-weight: 700; color: #dc3545; text-align: right; }
        </style>
    """, unsafe_allow_html=True)

    try:
        df = load_data()
    except Exception as e:
        st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
        return

    # --- 🔢 Data Processing Logic ---
    asset_items = []
    
    for index, row in df.iterrows():
        try:
            name_raw = str(row['AssetName'])
            
            # 1. Skip แถวที่ไม่ใช่ข้อมูลสินทรัพย์
            if pd.isna(row['Value']) or "Total" in name_raw or "Grand" in name_raw or name_raw == "nan":
                continue
            
            # 2. Filter: กรองเฉพาะ "Fund Saving" หรือ "Stock Saving" ออก (เก็บ Savings หลักไว้)
            name_lower = name_raw.lower()
            if "fund saving" in name_lower or "stock saving" in name_lower:
                continue

            icon = name_raw.strip()[0] 
            clean_name = name_raw.strip()[1:].strip()
            val = row['Value'] if pd.notnull(row['Value']) else 0
            inv = row['Invest'] if pd.notnull(row['Invest']) else 0
            gain_val = val - inv
            gain_pct = (gain_val / inv * 100) if inv != 0 else 0
            
            asset_items.append({
                "name": clean_name,
                "icon": icon,
                "value": val,
                "invest": inv,
                "gain_val": gain_val,
                "gain_pct": gain_pct
            })
        except Exception as e:
            continue

    # เรียงลำดับตามมูลค่า
    asset_items.sort(key=lambda x: x['value'], reverse=True)

    # คำนวณยอดรวมและ % ใหม่
    total_value = sum(item['value'] for item in asset_items)
    total_invest = sum(item['invest'] for item in asset_items)
    total_profit = total_value - total_invest
    total_profit_pct = (total_profit / total_invest * 100) if total_invest != 0 else 0
    
    for item in asset_items:
        pct = (item['value'] / total_value * 100) if total_value != 0 else 0
        item['percent'] = pct
        # สร้าง Label สำหรับกราฟวงกลม (ชื่อ + %)
        item['label'] = f"{item['name']} ({pct:.1f}%)"

    # --- 🏠 Display Section ---
    st.markdown("### 🚀 Portfolio Overview")

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">💎 Net Worth</div><div class="metric-value">฿ {total_value:,.0f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">💸 Total Invested</div><div class="metric-value" style="color:#444;">฿ {total_invest:,.0f}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Total Profit</div><div class="metric-value" style="color:#28a745;">+{total_profit:,.0f}</div><div class="metric-delta" style="color:#28a745;">▲ {total_profit_pct:.2f}%</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    col_main, col_side = st.columns([2, 1])

    with col_main:
        # 📊 Donut Chart (สไตล์ใหม่!)
        st.subheader("📊 Portfolio Composition")
        if asset_items:
            donut_df = pd.DataFrame(asset_items)

            # 1. สร้าง Base Chart
            base = alt.Chart(donut_df).encode(
                theta=alt.Theta("value", stack=True)
            )

            # 2. สร้างวงโดนัท (ปรับขนาดรูตรงกลาง innerRadius)
            pie = base.mark_arc(outerRadius=120, innerRadius=85).encode(
                color=alt.Color("name", legend=None), # ซ่อน Legend
                order=alt.Order("value", sort="descending"),
                tooltip=["name", "value", alt.Tooltip("percent", format=".1f")]
            )

            # 3. สร้างป้ายกำกับด้านนอก (ชื่อ + %)
            # หมายเหตุ: Altair ยังไม่มีเส้นชี้ (Leader line) ในตัว จึงวาง text ไว้ที่ radius วงนอกสุดแทน
            text_labels = base.mark_text(radius=145, fill="black").encode(
                text=alt.Text("label"),
                order=alt.Order("value", sort="descending")
            )

            # 4. สร้างข้อความตรงกลาง (Total Balance)
            center_value = alt.Chart(pd.DataFrame({'text': [f"฿ {total_value:,.0f}"]})).mark_text(
                radius=0, size=26, fontWeight='bold', color='#1a5d3a'
            ).encode(text='text')
            
            center_label = alt.Chart(pd.DataFrame({'text': ["Total Balance"]})).mark_text(
                radius=0, dy=25, size=14, color='#888' # dy คือเลื่อนลงมาข้างล่าง
            ).encode(text='text')

            # รวม Layer ทั้งหมดเข้าด้วยกัน
            chart = alt.layer(pie, text_labels, center_value, center_label).resolve_scale(
                theta="independent"
            ).properties(
                height=400 # เพิ่มความสูงให้กราฟมีที่ว่างสำหรับ Label ด้านนอก
            )

            st.altair_chart(chart, use_container_width=True)

        st.markdown("---")

        # Area Chart
        st.subheader("📈 Wealth Growth")
        chart_data = pd.DataFrame({
            "Date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01", "2024-06-01"]),
            "Net Worth": [total_value * 0.5, total_value * 0.6, total_value * 0.7, total_value * 0.8, total_value * 0.9, total_value],
            "Invested":  [total_invest * 0.8, total_invest * 0.85, total_invest * 0.9, total_invest * 0.95, total_invest, total_invest]
        })
        st.area_chart(chart_data.set_index("Date"), color=["#2E8B57", "#B0BEC5"])

    with col_side:
        st.subheader("💼 Assets Breakdown")
        
        for asset in asset_items:
            is_gain = asset['gain_val'] >= 0
            color_cls = "gain-text" if is_gain else "loss-text"
            arrow = "▲" if is_gain else "▼"
            sign = "+" if is_gain else ""
            
            st.markdown(f"""
            <div class="asset-item">
                <div style="display:flex; align-items:center;">
                    <div style="font-size:24px; margin-right:12px; background:#f0f2f5; padding:8px; border-radius:50%; width:45px; text-align:center;">
                        {asset['icon']}
                    </div>
                    <div>
                        <div class="asset-name">{asset['name']}</div>
                        <div class="asset-badge">{asset['percent']:.1f}% Port</div>
                    </div>
                </div>
                <div>
                    <div class="asset-val">฿ {asset['value']:,.0f}</div>
                    <div class="{color_cls}">
                        {arrow} {sign}{asset['gain_val']:,.0f} ({asset['gain_pct']:.1f}%)
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)