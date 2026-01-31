import google.generativeai as genai
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Config API Key (ควรซ่อนใน st.secrets ถ้าจะ deploy แต่วันนี้ใส่ตรงๆ หรือใช้ st.secrets ไปก่อนได้ครับ)
API_KEY = 'AIzaSyDEEoFjBMCx5kTer5XCMCj-dh9v_bPzcm0' 
genai.configure(api_key=API_KEY) 

def ask_warren_buffett(portfolio_data_text):
    """
    รับข้อมูลพอร์ต (Text) -> ส่งให้ AI วิจารณ์ -> คืนค่าเป็นคำแนะนำ
    """
    # 1. สร้าง Persona (System Instruction)
    buffett_persona = """
    คุณคือ Warren Buffett นักลงทุนแบบ Value Investor (VI) ในตำนาน
    นิสัย: สุขุม, มองเกมยาว, เกลียดความเสี่ยงที่ไม่จำเป็น, ชอบ Business ที่มี Moat (ปราการ) แข็งแกร่ง
    หน้าที่: วิจารณ์พอร์ตการลงทุนที่เห็นแบบตรงไปตรงมา สั้นกระชับ (Direct & Concise)
    
    สิ่งที่คุณต้องทำ:
    1. วิเคราะห์การกระจายความเสี่ยง (Diversification)
    2. เตือนถ้าเห็นหุ้นปั่น หรือ Sector ที่เสี่ยงเกินไป
    3. ให้คะแนนพอร์ต (Grade A-F)
    4. ปิดท้ายด้วย Quote เท่ๆ ของ Warren Buffett ที่เข้ากับสถานการณ์
    """
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=buffett_persona
    )
    
    # 2. สร้าง Prompt
    prompt = f"นี่คือหน้าตาพอร์ตการลงทุนของผมครับ ช่วยวิจารณ์หน่อย:\n\n{portfolio_data_text}"
    
    # 3. ยิง API
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ขออภัย ปู่ Buffett หลับอยู่ (Error: {e})"

def inject_custom_css():
    st.markdown("""
    <style>
        /* สไตล์จดหมายแบบ Premium */
        .advisor-card {
            background-color: #fdfbf7; /* สีครีมกระดาษ */
            border: 1px solid #e8e1d5;
            border-radius: 15px;
            padding: 40px;
            font-family: 'Sarabun', 'Georgia', serif; /* ฟอนต์อ่านง่ายดูแพง */
            color: #2c3e50;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            margin-top: 20px;
            position: relative;
        }
        .advisor-header {
            display: flex;
            align-items: center;
            border-bottom: 2px solid #1a5d3a; /* เส้นเขียวเข้ม */
            padding-bottom: 20px;
            margin-bottom: 25px;
        }
        .advisor-avatar {
            font-size: 60px;
            margin-right: 20px;
            background: #e8f5e9;
            width: 90px; height: 90px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 50%;
            border: 3px solid #1a5d3a;
        }
        .advisor-name {
            font-size: 24px;
            font-weight: 800;
            color: #1a5d3a;
            margin-bottom: 5px;
        }
        .advisor-role {
            font-size: 14px;
            color: #868e96;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .advisor-body {
            font-size: 16px;
            line-height: 1.8;
            color: #343a40;
        }
        .quote-icon {
            font-size: 40px; color: #ced4da; opacity: 0.5; position: absolute; right: 40px; top: 40px;
        }
        
        /* การ์ดสถิติเล็กๆ */
        .stat-badge {
            background: white; border: 1px solid #eee; 
            padding: 10px 15px; border-radius: 8px; 
            text-align: center; font-size: 13px; font-weight: 600; color: #555;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
    </style>
    """, unsafe_allow_html=True)
# ===========================
# Load data
# ===========================  
@st.cache_data(ttl=600)
def load_portfolio_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="rebalance", skiprows=1)
    df = df.iloc[:10, 6:11]
    df.columns = ['AssetName', 'Invest', 'Value', 'GainLoss_Text', 'Portion']
    
    cols_to_num = ['Invest', 'Value']
    for col in cols_to_num:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
    return df

@st.cache_data(ttl=600)
def load_pyramid_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="rebalance", skiprows=1)
    df = df.iloc[:4, 11:19]
    df.columns = ['Pyramid', 'Asset', 'Invest', 'Value', 'GainLoss', 'Portion (%)', 'Target(%)']
    df['GainLoss']= df['GainLoss']*100
    df['Portion (%)']=df['Portion (%)']*100
    df['Target(%)']=df['Target(%)']*100
    return df

# ===========================
# MAIN APP
# ===========================
def show():
    inject_custom_css()
    
    st.title("🧠 Wealth  Advisor")
    st.caption("AI-Powered Portfolio Analysis")
    
    # โหลดข้อมูล
    df = load_pyramid_data()
    
    if df.empty:
        st.error("⚠️ ไม่พบข้อมูลพอร์ต (กรุณาเช็คหน้า Pyramid ก่อนครับ)")
        return

    # --- ส่วนแสดงผลบน (Dashboard เล็กๆ) ---
    col_info, col_action = st.columns([1.5, 1])
    
    with col_info:
        st.markdown("##### Portfolio Overview")
        # สรุปตัวเลขให้ดูหน่อย
        total_val = df['Value'].sum()
        top_layer = df.sort_values(by='Portion (%)', ascending=False).iloc[0]['Pyramid']
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-badge'>Total Value<br><span style='color:#1a5d3a; font-size:16px;'>฿{total_val/1000:,.1f}k</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-badge'>Top Allocation<br><span style='color:#e67e22; font-size:16px;'>{top_layer}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-badge'>Assets<br><span style='color:#2980b9; font-size:16px;'>{len(df)} รายการ</span></div>", unsafe_allow_html=True)
        
        with st.expander("🔍 ดูข้อมูลดิบที่ส่งให้ AI"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    with col_action:
        st.markdown("#### 💡AI Consultant")
        st.write("Get personalized advice based on Value Investing principles.")
        
        analyze_btn = st.button("🎩Analyze Portfolio", type="primary", use_container_width=True)

    st.write("---")

    # --- ส่วนแสดงผลลัพธ์ (Letter) ---
    if analyze_btn:
        with st.spinner("⏳ กำลังวิเคราะห์..."):
            advice = ask_warren_buffett(df)
            
            # แสดงผลแบบการ์ดสวยงาม
            st.markdown(f"""
            <div class="advisor-card">
                <div class="quote-icon">❝</div>
                <div class="advisor-header">
                    <div class="advisor-avatar">🎩</div>
                    <div>
                        <div class="advisor-name">Warren Buffett (AI)</div>
                        <div class="advisor-role">Legendary Value Investor</div>
                    </div>
                </div>
                <div class="advisor-body">
                    {advice}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        # State เริ่มต้น (ยังไม่กด)
        st.info("👋 ผมพร้อมให้คำแนะนำครับ กดปุ่มข้างบนได้เลย ไม่ต้องเกรงใจ")