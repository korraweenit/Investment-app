
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from streamlit_gsheets import GSheetsConnection  
from datetime import timedelta
import datetime
import utils

# st.set_page_config(page_title="Wealth Command Center", layout="wide")

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
        df=df[df['Net Value (THB)']!=0]
        df = df.sort_values('Date')
        return df
    except Exception as e:
        st.error(f'Error loading transaction : {e}')
        return None
    
def handle_update(rebalance_df):
    try:
        current_value=rebalance_df['Value'].sum()
        current_cost=rebalance_df['Invest'].sum()
        transactions=load_transaction_history()

        new_hx_df=utils.update_portfolio_hx(
            current_value, current_cost, transactions,
            hx_sheet='Portfolio_Hx',benchmark_ticker='SPY'
        )
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
def display_Hxchart(rebalance_df):
    def display_Hxchart(hx_df):
        st.subheader("📈 My Portfolio vs S&P 500")
        if len(hx_df)<2:
            st.info("⏳ รอสะสมข้อมูลอีกสัก 1-2 วัน กราฟจะเริ่มวาดเส้นให้เห็นครับ")
            return 
        plot_df=hx_df.copy()
        plot_df['Date']=pd.to_datetime(plot_df['Date'])

        myport_1=plot_df['My_Stock_Value'].iloc[0]
        sp500_1=plot_df['Strategy_SP500_Value'].iloc[0]
        cost_1=plot_df['My_Stock_Cost'].iloc[0]

        plot_df['myport_%']=((plot_df['My_Stock_Value']-myport_1)/myport_1)*100
        plot_df['sp500_%']=((plot_df['Strategy_SP500_Value']-sp500_1)/sp500_1)*100
        plot_df['cost_%']=((plot_df['My_Stock_Cost']-cost_1)/cost_1)*100

        fig=px.line(plot_df,
            x='Date',
            y=['myport_%','sp500_%', 'cost_%'],
            color_discrete_map={'myport_%': '#00CC96','sp500_%': '#EF553B', "cost_%" : "#4B4949" }              
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

    #display
    col1,col2=st.columns([3,1])
    with col1:
        st.info("💡 Tip: Please fill the transactions before update")
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
def show():
    st.title("US stock")
    st.markdown("---")
    
    df = load_data()

    df=display_metrics_filter(df)
    st.markdown("---")

    sort_df = display_sort(df)
    display_table(sort_df)
    st.markdown("---")

    display_graph(df)
    st.markdown("---")
    
    display_Hxchart(df)




