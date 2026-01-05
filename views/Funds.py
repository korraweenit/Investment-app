import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Fund summary", skiprows=5)
    return df

def show():
    st.markdown("""
        <style>
        /* ===== Global Styles ===== */
        .stApp { 
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* ===== Top NAV Card ===== */
        .nav-card {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
            border-radius: 24px;
            padding: 32px;
            color: white;
            box-shadow: 
                0 20px 40px rgba(22, 163, 74, 0.2),
                0 0 0 1px rgba(255,255,255,0.1) inset;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }
        
        .nav-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        }
        
        .nav-title { 
            font-size: 13px; 
            opacity: 0.85; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .nav-value { 
            font-size: 42px; 
            font-weight: 800; 
            margin: 0;
            line-height: 1.1;
            letter-spacing: -1px;
        }
        
        .nav-badge {
            background: rgba(255,255,255,0.25);
            backdrop-filter: blur(10px);
            padding: 8px 16px; 
            border-radius: 16px; 
            font-size: 14px; 
            font-weight: 700;
            display: inline-block;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .nav-footer {
            display: flex; 
            justify-content: space-between; 
            margin-top: 24px; 
            padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.15);
        }
        
        .nav-stat-label {
            font-size: 11px; 
            opacity: 0.75;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        
        .nav-stat-value {
            font-size: 18px; 
            font-weight: 700;
        }
        
        /* ===== Section Header ===== */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 800;
            color: #1e293b;
            margin: 0;
        }
        
        .month-badge {
            background: white;
            color: #64748b;
            font-weight: 600;
            font-size: 12px;
            padding: 8px 16px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        
        /* ===== Fund Cards ===== */
        .fund-card {
            background: white;
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 
                0 1px 3px rgba(0,0,0,0.04),
                0 4px 12px rgba(0,0,0,0.03);
            border: 1px solid rgba(226, 232, 240, 0.8);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .fund-card:hover { 
            transform: translateY(-4px);
            box-shadow: 
                0 4px 12px rgba(0,0,0,0.08),
                0 12px 28px rgba(0,0,0,0.06);
        }
        
        /* === IMPROVED Fund Icon === */
        .fund-icon {
            width: 56px; 
            height: 56px;
            border-radius: 18px;
            display: flex; 
            align-items: center; 
            justify-content: center;
            font-weight: 800; 
            font-size: 24px;
            margin-right: 16px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        
        /* Gradient variations */
        .fund-icon-blue {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .fund-icon-purple {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .fund-icon-green {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .fund-icon-orange {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }
        
        /* Icon shine effect */
        .fund-icon::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
        }
        
        .fund-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .fund-name-section {
            display: flex;
            align-items: center;
        }
        
        .fund-name { 
            font-weight: 800; 
            font-size: 17px; 
            color: #0f172a;
            line-height: 1.3;
        }
        
        .fund-alloc {
            text-align: right;
        }
        
        .fund-alloc-label {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .fund-alloc-value {
            font-weight: 800;
            color: #475569;
            font-size: 16px;
        }
        
        /* Fund Stats */
        .fund-stats {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 16px;
        }
        
        .stat-group {
            flex: 1;
        }
        
        .stat-label { 
            font-size: 11px; 
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .stat-value { 
            font-size: 16px; 
            font-weight: 700; 
            color: #1e293b;
            line-height: 1.3;
        }
        
        .stat-divider {
            margin-top: 12px;
        }
        
        /* Profit/Loss Colors */
        .profit-pos { 
            color: #16a34a; 
            font-weight: 700; 
        }
        
        .profit-neg { 
            color: #dc2626; 
            font-weight: 700; 
        }
        
        .badge-pos {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            color: #15803d;
            padding: 6px 12px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 800;
            display: inline-block;
            border: 1px solid rgba(22, 163, 74, 0.2);
        }
        
        .badge-neg {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            color: #dc2626;
            padding: 6px 12px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 800;
            display: inline-block;
            border: 1px solid rgba(220, 38, 38, 0.2);
        }
        
        /* === NEW: Graph Button === */
        .graph-button-container {
            display: flex;
            justify-content: flex-end;
            padding-top: 12px;
            border-top: 1px solid #f1f5f9;
        }
        
        /* Alignment */
        .align-right {
            text-align: right;
        }
        </style>
    """, unsafe_allow_html=True)

    # Load data
    df = load_data()
    df['%'] = df['%'] * 100
    
    total_val = df.loc[4, 'Value']
    total_cost = df.loc[4, 'Invest']
    total_pl = df.loc[4, 'P/L']
    total_pl_pct = df.loc[4, '%']
    
    df = df.iloc[:-1]
    
    # กำหนด icon และสีแต่ละกองทุน
    fund_config = {
        'SCBGQUALE': {'icon': '🌍', 'color_class': 'fund-icon-white'},
        'SCBCEHE': {'icon': '🧧', 'color_class': 'fund-icon-purple'},
        'NDQ100': {'icon': '🚀', 'color_class': 'fund-icon-green'},
        'S&P500': {'icon': '🗽', 'color_class': 'fund-icon-green'},
    }
    
    # ===== UI Section =====
    
    # 1. Top NAV Card
    st.markdown(f"""
        <div class="nav-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; position:relative; z-index:1;">
                <div>
                    <div class="nav-title">Net Asset Value</div>
                    <div class="nav-value">฿{total_val:,.2f}</div>
                </div>
                <div class="nav-badge">▲ {total_pl_pct:.2f}%</div>
            </div>
            <div class="nav-footer">
                <div>
                    <div class="nav-stat-label">Total Cost</div>
                    <div class="nav-stat-value">฿{total_cost:,.2f}</div>
                </div>
                <div class="align-right">
                    <div class="nav-stat-label">Total P/L</div>
                    <div class="nav-stat-value">+฿{total_pl:,.2f}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Section Header
    current_month = pd.Timestamp.now().strftime('%b %Y')
    st.markdown(f"""
        <div class="section-header">
            <h2 class="section-title">📊 Monthly Investment Record</h2>
            <div class="month-badge">{current_month}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. Fund Cards
    for idx, item in df.iterrows():
        is_pos = item['P/L'] >= 0
        color_cls = "profit-pos" if is_pos else "profit-neg"
        badge_cls = "badge-pos" if is_pos else "badge-neg"
        sign = "+" if is_pos else ""
        
        # ดึง config ของกองทุนนี้
        config = fund_config.get(item['Name'], {'icon': '💰', 'color_class': 'fund-icon-blue'})
        icon = config['icon']
        color_class = config['color_class']

        st.markdown(f"""
            <div class="fund-card">
                <!-- Header -->
                <div class="fund-header">
                    <div class="fund-name-section">
                        <div class="fund-icon {color_class}">{icon}</div>
                        <div class="fund-name">{item['Name']}</div>
                    </div>
                    <div class="fund-alloc">
                        <div class="fund-alloc-label">Allocation</div>
                        <div class="fund-alloc-value">{item['Portion']:.1f}%</div>
                    </div>
                </div>   
                <!-- Stats -->
                <div class="fund-stats">
                    <div class="stat-group">
                        <div class="stat-label">Invested</div>
                        <div class="stat-value">฿{item['Invest']:,.0f}</div>
                        <div class="stat-divider">
                            <div class="stat-label">Profit/Loss</div>
                            <div class="{color_cls}" style="font-size:15px;">{sign}฿{item['P/L']:,.0f}</div>
                        </div>
                    </div>
                    <div class="stat-group align-right">
                        <div class="stat-label">Current Value</div>
                        <div class="stat-value">฿{item['Value']:,.0f}</div>
                        <div class="stat-divider">
                            <span class="{badge_cls}">
                                {sign}{item['%']:.2f}%
                            </span>
                        </div>
                    </div>
                </div>   
                <!-- Graph Button -->
                <div class="graph-button-container">
        """, unsafe_allow_html=True)
        
        # Streamlit button (อยู่นอก HTML)
        if st.button(f"📈 Show Graph", key=f"graph_{item['Name']}", type="secondary", use_container_width=False):
            st.session_state[f'show_graph_{item["Name"]}'] = True
            # TODO: คุณจะเขียน logic แสดงกราฟที่นี่
            st.info(f"กำลังแสดงกราฟของ {item['Name']}...")
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)

