import google.generativeai as genai
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ===========================
# AI function
# ===========================  
#Config API Key (ควรซ่อนใน st.secrets ถ้าจะ deploy แต่วันนี้ใส่ตรงๆ หรือใช้ st.secrets ไปก่อนได้ครับ)
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY) 

def ask_warren_buffett(user_input, history_messages, uploaded_file=None, portfolio_df=None):
    """
    ฟังก์ชันเดียวจบ: รับคำถาม + ประวัติ + ไฟล์ -> ส่งคืนคำตอบสไตล์ปู่
    """
    # A. สร้าง Persona
    buffett_persona = """
    Act as: "The Modern Intelligent Investor" (นักลงทุน VI ยุคใหม่ ผู้ยึดมั่นในหลักการแต่ทันโลก)

    **Character Profile:**
    คุณคือนักลงทุนสายปัจจัยพื้นฐาน (Fundamentalist) ที่มีบุคลิก "สุขุม, เยือกเย็น, และมองเกมยาว (Long-term Horizon)" คุณเกลียดการเก็งกำไรอย่างไร้เหตุผล (Speculation) แต่คุณก็เข้าใจธุรกิจยุคใหม่ (Tech/Innovation) ตราบใดที่มันมี **"Economic Moat" (ป้อมปราการทางธุรกิจ)** ที่แข็งแกร่ง

    **Your Mission:**
    วิจารณ์พอร์ตการลงทุนของฉัน (Portfolio Audit) แบบ "ขวานผ่าซาก" (Brutally Honest) ไม่ต้องรักษาน้ำใจ เน้นเนื้อหา กระชับ และตรงประเด็น

    **Analysis Framework (ขั้นตอนการวิเคราะห์):**

    1.  **The Moat Test (ตรวจสอบป้อมปราการ):**
        * กวาดสายตาดูหุ้นรายตัว ตัวไหนที่มี "อำนาจการต่อรองราคา" (Pricing Power) หรือ "คู่แข่งโค่นยาก" ให้ชม
        * ตัวไหนที่เป็น Commodity, หุ้นปั่น (Penny Stock), หรือธุรกิจตะวันตกดิน ให้ **"Red Flag"** ทันที

    2.  **Risk & Diversification Check:**
        * วิเคราะห์การกระจายความเสี่ยง: ฉัน "Put too many eggs in one basket" หรือไม่?
        * หรือฉันกระจายเยอะเกินไปจนมั่ว (Di-worsification)?

    3.  **The Verdict (การให้คะแนน):**
        * ให้เกรดพอร์ตของฉัน (Grade **A, B, C, D, หรือ F**)
        * *เกณฑ์:* A = พอร์ตแกร่งดั่งหินผา, F = พอร์ตนักพนัน

    4.  **Buffett's Wisdom:**
        * ปิดท้ายด้วย **Quote ของ Warren Buffett** ที่เสียดแทงใจดำ หรือเข้ากับสถานการณ์พอร์ตของฉันที่สุด (พร้อมแปลไทย)

    **Tone:**
    * สั้น (Concise), คม (Sharp), เตือนสติ (Warning).
    * **Language:** Respond in Thai (ตอบเป็นภาษาไทย).

    **Initialization:**
    * เริ่มต้นด้วยการแนะนำตัวสั้นๆ ตามคาแรคเตอร์ และถามฉันว่า: **"วางพอร์ตของคุณลงบนโต๊ะสิครับ... บอกชื่อหุ้น, สัดส่วน (%), และราคาต้นทุนของคุณมา ผมจะดูให้ว่าคุณกำลัง 'ลงทุน' หรือ 'เล่นพนัน'"**
        """

    try:
        # B. เตรียม Prompt
        # แปลงประวัติการคุยเป็น Text ก้อนเดียว
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history_messages])
        
        prompt_parts = []
        
        if portfolio_df is not None and not portfolio_df.empty:
            # แปลงตารางเป็น String เพื่อให้ AI อ่านรู้เรื่อง
            port_str = portfolio_df.to_string(index=False)
            prompt_parts.append(f"📊 ข้อมูลพอร์ตปัจจุบันของผู้ใช้ (Live Data):\n{port_str}\n")
            prompt_parts.append("(กรุณาใช้ข้อมูลข้างบนนี้ประกอบการวิเคราะห์ หากผู้ใช้ถามถึงพอร์ต)")

        # ถ้ามีไฟล์ -> แนบไฟล์
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            file_part = {"mime_type": uploaded_file.type, "data": bytes_data}
            prompt_parts.append("นี่คือเอกสารแนบ:")
            prompt_parts.append(file_part)
        
        # ใส่บริบท
        prompt_parts.append(f"ประวัติการสนทนา:\n{history_text}")
        prompt_parts.append(f"คำถามล่าสุด: {user_input}")
        prompt_parts.append("คำตอบของ Warren Buffett:")

        # C. เรียก Model
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=buffett_persona
        )
        
        response = model.generate_content(prompt_parts)
        return response.text

    except Exception as e:
        return f"ขออภัย ปู่ Buffett หลับอยู่ (Error: {e})"

def analyze_uploaded_file(uploaded_file, prompt_text):
    """
    รับไฟล์ (PDF/Image) -> ส่งให้ AI อ่าน -> คืนค่าคำตอบ
    """
    # 1. อ่านไฟล์เป็น Bytes
    bytes_data = uploaded_file.getvalue()

    # 2. กำหนดประเภทไฟล์ (MIME Type)
    mime_type = uploaded_file.type # เช่น 'image/png' หรือ 'application/pdf'
    
    file_part = {
        "mime_type": mime_type,
        "data": bytes_data
    }
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        # ส่งไปเป็น List: [ข้อความคำสั่ง, ข้อมูลไฟล์]
        response = model.generate_content([prompt_text, file_part])
        return response.text
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

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
    df = df.iloc[:3, 11:19]
    df.columns = ['Pyramid', 'Asset', 'Invest', 'Value', 'GainLoss', 'Portion (%)', 'Target(%)']
    df['GainLoss']= df['GainLoss']*100
    df['Portion (%)']=df['Portion (%)']*100
    df['Target(%)']=df['Target(%)']*100
    return df

# ===========================
# MAIN APP
# ===========================
def inject_custom_css():
    st.markdown("""
    <style>
        /* สไตล์จดหมายแบบ Premium */
        .advisor-card {
            background-color: #fdfbf7;
            border: 1px solid #e8e1d5;
            border-radius: 15px;
            padding: 30px; /* ลดขอบลงนิดนึงจาก 40 */
            font-family: 'Sarabun', 'Thonburi', 'Georgia', serif; /* เพิ่มฟอนต์ไทย */
            color: #2c3e50;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            margin-top: 20px;
            margin-bottom: 20px;
            position: relative;
        }
        /* ... (Header สไตล์เดิม ไม่ต้องแก้) ... */
        .advisor-header {
            display: flex;
            align-items: center;
            border-bottom: 1px solid #1a5d3a; /* เส้นบางลงหน่อย */
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .advisor-avatar {
            font-size: 50px;
            margin-right: 15px;
            background: #e8f5e9;
            width: 70px; height: 70px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 50%;
            border: 2px solid #1a5d3a;
        }
        .advisor-name { font-size: 20px; font-weight: 800; color: #1a5d3a; margin: 0; }
        .advisor-role { font-size: 12px; color: #868e96; text-transform: uppercase; letter-spacing: 1px; }
        
        /* 🔥 จุดที่แก้: ปรับ Body ให้แน่นขึ้น */
        .advisor-body {
            font-size: 16px;
            line-height: 1.5; /* ลดจาก 1.8 -> 1.5 (ชิดขึ้น) */
            color: #343a40;
            white-space: pre-line; /* ใช้ pre-line แทน pre-wrap (ช่วยยุบช่องว่างเกินจำเป็น) */
        }
        
        /* แถม: ทำให้ List (รายการข้อๆ) ชิดขึ้นด้วย */
        .advisor-body ul, .advisor-body ol { margin-top: 5px; margin-bottom: 5px; }
        .advisor-body li { margin-bottom: 5px; }

        .quote-icon {
            font-size: 40px; color: #ced4da; opacity: 0.3; position: absolute; right: 30px; top: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_buffett_card(text):
    html = f"""
    <div class="advisor-card">
        <div class="quote-icon">❝</div>
        <div class="advisor-header">
            <div class="advisor-avatar">🎩</div>
            <div>
                <div class="advisor-name">Warren Buffett (AI)</div>
                <div class="advisor-role">Legendary Value Investor</div>
            </div>
        </div>
        <div class="advisor-body">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def show():
    inject_custom_css()
    df = load_pyramid_data()
    # Sidebar: ส่วนอัปโหลดและควบคุม
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4205/4205906.png", width=80)
        st.title("Wealth Advisor")
        
        if not df.empty:
            st.success(f"✅ Data Loaded: {len(df)} รายการ")
            with st.expander("แอบดูข้อมูล (Raw Data)"):
                st.dataframe(df, hide_index=True)
        else:
            st.warning("⚠️ ยังไม่พบข้อมูลพอร์ต")
        
        st.markdown("---")
        uploaded_file = st.file_uploader("📂 Upload Portfolio / Financial Stmt.", type=["pdf", "png", "jpg"])
        
        if uploaded_file:
            st.success(f"Loaded: {uploaded_file.name}")
            if uploaded_file.type in ["image/png", "image/jpeg"]:
                st.image(uploaded_file, caption="Preview", use_column_width=True)

        st.markdown("---")
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.rerun()

    # Main Area: Chat Interface
    st.markdown("#### 💬 Consult with the Legend")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "สวัสดีครับ... การลงทุนคือการวิ่งมาราธอน ไม่ใช่การวิ่งสปรินต์ วันนี้มีพอร์ตหรือหุ้นตัวไหนอยากให้ผมช่วยวิเคราะห์ไหมครับ?"}
        ]

    # Loop แสดงข้อความเก่า
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # ข้อความฝั่งเรา (แสดงแบบปกติ หรือ Chat bubble)
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            # ข้อความฝั่ง AI (แสดงแบบการ์ดจดหมายสุดหรู)
            render_buffett_card(msg["content"])

    # Input รับข้อความใหม่
    if user_input := st.chat_input("พิมพ์คำถาม หรือขอคำแนะนำได้เลย..."):
        # 1. แสดงข้อความเรา
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. AI คิดและแสดงผล
        with st.spinner("Writing advice..."):
            ai_reply = ask_warren_buffett(user_input, st.session_state.messages, uploaded_file,portfolio_df=df)
            
            # แสดงการ์ดจดหมาย
            render_buffett_card(ai_reply)
            
            # บันทึก
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
