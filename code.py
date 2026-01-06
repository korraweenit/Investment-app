import streamlit as st
import pandas as pd

st.subheader("Portfolio Comparison (P/E Ratio)")

# สร้างข้อมูล: หุ้น 3 ตัว กับค่า P/E ของมัน
# สังเกตว่าเรากำหนด index เป็นชื่อหุ้น (A, B, C) ไม่ใช่ตัวเลข 0,1,2
pe_data = pd.DataFrame(
    [15.5, 22.1, 8.5],
    index=['Stock A', 'Stock B', 'Stock C'], 
    columns=['P/E Ratio']
)

st.bar_chart(pe_data)

st.subheader("Hospital Admissions by Department")
dept_data = pd.DataFrame(
    [[120, 45, 80],[1,1,1]],
    index=['OPD', 'ER', 'IPD'],
    columns=['Patients','Doctor']
)
st.bar_chart(dept_data)