import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

def update_portfolio_hx(current_value, current_total_cost, transactions_df,hx_sheet='Portfolio_Hx',benchmark_ticker='SPY'):
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        hx_df = conn.read(worksheet=hx_sheet)
        hx_df['Date'] = pd.to_datetime(hx_df['Date']).dt.tz_localize(None)
    except:
        hx_df=pd.DataFrame(columns=['Date','My_Stock_Cost','My_Stock_Value','Strategy_SP500_Value',"SPY_Shares"])
    
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 2. เช็คว่า "วันนี้" มีข้อมูลหรือยัง?
   
    today_mask = hx_df['Date'].dt.strftime('%Y-%m-%d') == today_str
    
    if today_mask.any():
        hx_df.loc[today_mask, 'My_Stock_Cost'] = current_total_cost
        hx_df.loc[today_mask, 'My_Stock_Value'] = current_value
    else:
        new_row=pd.DataFrame([{
        'Date': today_str, 
        'My_Stock_Cost': current_total_cost,
        'My_Stock_Value': current_value, 
        'Strategy_SP500_Value':0,
        'SPY_Shares': 0
        }])
        new_row['Date'] = pd.to_datetime(new_row['Date']).dt.tz_localize(None)
        hx_df=pd.concat([hx_df,new_row], ignore_index=True)

    hx_df = hx_df.sort_values(by='Date').reset_index(drop=True)

    spy_share_1=hx_df['SPY_Shares'].iloc[0]
    date_1=hx_df['Date'].iloc[0]

    trans=transactions_df.copy()
    trans['Date']=pd.to_datetime(trans['Date']).dt.tz_localize(None)
    trans=trans[trans['Date']> date_1]

    spy_price_df=yf.download('SPY', start=date_1, end=datetime.datetime.now()+datetime.timedelta(days=1), progress=False)['Close']
    spy_price_df.index=spy_price_df.index.tz_localize(None)

    for i, row in hx_df.iterrows():
        if i==0: continue

        rel_trans=trans[trans['Date']<= row['Date']]
        add_share=0.0
        for _, t_row in rel_trans.iterrows():
            add_share+=t_row['Total Value ($)']/spy_price_df.asof(t_row['Date'])
            
        spy_share=  spy_share_1 + add_share
        current_benchmark_value= spy_share*(spy_price_df.asof(row['Date']))

        hx_df.at[i, 'Strategy_SP500_Value']= current_benchmark_value
        hx_df.at[i,'SPY_Shares']=spy_share
    
    hx_df['Date'] = hx_df['Date'].dt.strftime('%Y-%m-%d')
    conn.update(worksheet='Portfolio_Hx', data=hx_df)

    return hx_df

