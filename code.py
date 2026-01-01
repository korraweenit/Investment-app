import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from streamlit_gsheets import GSheetsConnection  
from datetime import timedelta
import datetime

st.set_page_config(page_title="Wealth Command Center", layout="wide")

# ===========================
# DATA 
# ===========================
@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="rebalance", skiprows=14)
    df=df[~df['US stock'].str.lower().str.contains('total')]

    return df

# sp500
@st.cache_data(ttl=600)
def load_transaction_history():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df=conn.read(worksheet='Buying track',skiprows=6)
        df['Date']=pd.to_datetime(df['Date'],format='%d/%m/%Y')
        df=df[df['Buy/Sell']=='Buy']
        df = df.sort_values('Date')
        return df
    except Exception as e:
        st.error(f'Error loading transaction : {e}')
        return None
    
def update_portfolio_hx(current_value, current_total_cost, transactions_df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        hx_df = conn.read(worksheet='Portfolio_Hx')
        hx_df['Date'] = pd.to_datetime(hx_df['Date']).dt.tz_localize(None)
    except:
        hx_df=pd.DataFrame(columns=['Date','My_Cost','My_Stock_Value','Strategy_SP500_Value',"SPY_Shares"])
    
    today = datetime.datetime.now().date()

    #หากกดซ้ำ ให้ลบของวันนี้ทิ้งก่อน
    if not hx_df.empty:
        hx_df=hx_df[hx_df['Date'].dt.date != today]
    
    st.toast(f"📝 กำลังบันทึกข้อมูลของวันที่ {today}...", icon="💾")
    if hx_df.empty:
        #ดูซ้ำ##### 
        current_spy_price = yf.Ticker('SPY').history(period='5d')['Close'].iloc[-1]
        spy_share=current_value/current_spy_price

        new_row = pd.DataFrame([{
                'Date': today,
                'My_Stock_Value':current_value ,
                'Strategy_SP500_Value': current_value,
                'SPY_Shares': spy_share,
                'My_Cost': current_total_cost
            }])
        conn.update(worksheet='Portfolio_Hx', data=new_row)
        return new_row
    else:
        new_row=pd.DataFrame([{
        'Date': today, 
        'My_Cost': current_total_cost,
        'My_Stock_Value': current_value, 
        'Strategy_SP500_Value':0,
        'SPY_Shares': 0
        }])
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
            ifspy_value= spy_share*(spy_price_df.asof(row['Date']))

            hx_df.at[i, 'Strategy_SP500_Value']= ifspy_value
            hx_df.at[i,'SPY_Shares']=spy_share
        
        hx_df['Date'] = hx_df['Date'].dt.strftime('%Y-%m-%d')
        conn.update(worksheet='Portfolio_Hx', data=hx_df)

        return hx_df
    
def handle_update(rebalance_df):
    try:
        current_value=rebalance_df['Value'].sum()
        current_cost=rebalance_df['Invest'].sum()
        transactions=load_transaction_history()

        new_hx_df=update_portfolio_hx(current_value, current_cost, transactions)
        return new_hx_df
    
    except Exception as e:
        st.error(f"⚠️ Error to update: {e}")
        return None

# ===========================
# UI COMPONENTS
# ===========================
def display_metrics_filter(df):
    col1, col2, col3=st.columns([1.5,1,5])
    with col1:
        st.subheader("📊 Overview")
    with col2:
        types = ['All']+df['Type'].unique().tolist()    
        selected_type = st.selectbox("Type", types,label_visibility="collapsed")
        filtered_df = df.copy()
        if selected_type !='All':
            filtered_df=filtered_df[filtered_df['Type']==selected_type]
    
    df=filtered_df
    
    Invest=df['Invest'].sum()
    Money=df['Value'].sum()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Stocks" , len(df))
    with col2:
        st.metric("💰 Total Invest",f"$ {Invest:,.2f}" )
    with col3:
        st.metric("💵 Present Value",f"$ {Money:,.2f}" )
    with col4:
        st.metric("📈 Profit/Loss",f"$ {(Money-Invest):,.2f}",delta=f"{(((Money-Invest)/Invest)*100):+.2f}%")

    return filtered_df

def display_table(df):
    st.dataframe(
        df.style.format({
            'Value': '${:,.2f}',
            'Invest': '${:,.2f}',
            'Profit/loss': '${:,.2f}',
            '%':'{:.2%}'
        }),
        use_container_width=True
    )

def display_sort(df):
    st.subheader("📋 Portfolio Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox( "Sort by", [ 'Value', 'Invest', 'Profit/loss'])
    with col2:
        sort_order=st.radio("Order",['High->Low','Low->High'],horizontal=True)
        ascending = (sort_order == 'Low->High')
    with col3:
        show_all = st.checkbox("All columns", value=True)
        if not show_all:
            cols_to_show = st.multiselect(
                "Select Columns",
                df.columns.tolist(),
                default=['US stock', 'Type','Invest', 'Value', 'Profit/loss']
            )
            df=df[cols_to_show]
    df=df.sort_values(sort_by,ascending=ascending)
    
    return df

def display_graph(df):
    # make fx show graph
    def create_piechart(df):
        fig=px.pie(df, values='Portion',names='US stock',title='🍰 Stock Allocation',hole=0.4)
        fig.update_traces(textposition='inside',textinfo='percent+label' )
        return fig
    
    def create_comparechart(df):
        type_summary=df.groupby('Type').agg({'Value':'sum','Invest':'sum','Profit/loss':'sum'}).reset_index()
        fig=go.Figure(data=[
            go.Bar( name='Total invest', x=type_summary['Type'],y=type_summary['Invest']),
            go.Bar(name='Current Value', x=type_summary['Type'],y=type_summary['Value'])
        ])
        fig.update_layout(
        title='📊 Tech vs Defensive Comparison',
        xaxis_title='Type',
        yaxis_title='Value ($)',
        barmode='group')

        return fig
        #sp500

    # display graph
    st.subheader("🧠 Analytics")
    col1,col2=st.columns(2)
    with col1:
        piechart=create_piechart(df)
        st.plotly_chart(piechart, use_container_width=True)
    with col2:
        type_fig=create_comparechart(df)
        st.plotly_chart(type_fig, use_container_width=True)
#sp500
def display_Hxchart_button(rebalance_df):
    def display_Hxchart(hx_df):
        st.subheader("📈 My Portfolio vs S&P 500")
        if len(hx_df)<2:
            st.info("⏳ รอสะสมข้อมูลอีกสัก 1-2 วัน กราฟจะเริ่มวาดเส้นให้เห็นครับ")
            return 
        plot_df=hx_df.copy()
        plot_df['Date']=pd.to_datetime(plot_df['Date'])

        myport_1=plot_df['My_Stock_Value'].iloc[0]
        sp500_1=plot_df['Strategy_SP500_Value'].iloc[0]
        cost_1=plot_df['My_Cost'].iloc[0]

        plot_df['myport_%']=((plot_df['My_Stock_Value']-myport_1)/myport_1)*100
        plot_df['sp500_%']=((plot_df['Strategy_SP500_Value']-sp500_1)/sp500_1)*100
        plot_df['cost_%']=((plot_df['My_Cost']-cost_1)/cost_1)*100

        fig=px.line(plot_df,
            x='Date',
            y=['myport_%','sp500_%','cost_%'],
            color_discrete_map={'myport_%': '#00CC96','sp500_%': '#EF553B', 'cost_%': '#7F7F7F'  }              
        )
        # fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

    #display
    col1,col2=st.columns([3,1])
    with col1:
        st.info("💡 Tip: กรอก Transaction ให้ครบก่อนกดอัปเดตนะครับ")
    with col2:
        update_btn=st.button("💾 Update Data",type='primary',use_container_width=True)
    if update_btn:
        new_hx_df=handle_update(rebalance_df)
        display_Hxchart(new_hx_df)
    else:
        conn = st.connection("gsheets", type=GSheetsConnection)
        hx_df= conn.read(worksheet='Portfolio_Hx')
        display_Hxchart(hx_df)
# ===========================
# MAIN APP
# ===========================
def main():
    st.title("👨‍⚕️ Investment Dashboard")
    st.markdown("---")
    
    df = load_data()

    df=display_metrics_filter(df)
    st.markdown("---")

    sort_df = display_sort(df)
    display_table(sort_df)
    st.markdown("---")

    display_graph(df)
    st.markdown("---")
    
    display_Hxchart_button(df)

if __name__ == "__main__":
    main() 
    


# ===========================
# Unused fx
# ===========================
@st.cache_data(ttl=3600)
def get_sp500_data(startdate):
    spy=yf.download('SPY',start=startdate, progress=False)
    spy.index = spy.index.tz_localize(None)
    return spy['Close']

def create_benchmark(df):
    df=df.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    startdate=df['Date'].min()
    spy=get_sp500_data(startdate)

    df['sp500_price']=df['Date'].map(lambda x: spy.loc[x].item())
    df['sp500_share']=df['Total Value ($)']/df['sp500_price']
    df['sp500_cumshare']=df['sp500_share'].cumsum()
    df['sp500_cumprice']=df['sp500_cumshare']*df['sp500_price']
    df['my_cuminvest']=df['Total Value ($)'].cumsum()
    total_spy= df['sp500_share'].sum()*spy.iloc[-1]
    return total_spy

