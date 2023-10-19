import FinanceDataReader as fdr
from datetime import datetime, timedelta

import mplfinance as mpf
import matplotlib.pyplot as plt

import json
from streamlit_lottie import st_lottie
import streamlit as st

import pandas as pd

# JSON을 읽어 들이는 함수
def loadJSON(path):
    f = open(path, 'r')
    res = json.load(f)
    f.close()
    return res

# 로고 Lottie와 타이틀 출력
col1, col2 = st.columns([1,2])
with col1:
    lottie = loadJSON('lottie-stock-candle-loading.json')
    st_lottie(lottie, speed=1, loop=True, width=150, height=150)

with col2:
    ''
    ''
    st.title("정보 시각화")

# 시장 데이터를 읽어오는 함수들을 정의한다.
@st.cache_data
def getData(code, datestart, dateend):
    df = fdr.DataReader(code, datestart, dateend).drop(columns='Change')
    return df

@st.cache_data
def getSymbols(market="KOSPI", sort="Marcap"):
    df = fdr.StockListing("KOSPI") # 코스피 종목 확인
    ascending = False if sort == 'Marcap' else True # 내림차순
    df.sort_values(by=[sort], ascending=ascending, inplace=True)

    return df[['Code','Name','Market']]
    
# 세션 상태를 초기화 한다.
if 'ndays' not in st.session_state:
    st.session_state['ndays'] = 30

if 'code_index' not in st.session_state:
    st.session_state['code_index'] = 0

if 'chart_style' not in st.session_state:
    st.session_state['chart_style'] = 'default'

if 'volume' not in st.session_state:
    st.session_state['volume'] = True

# 사이드바에서 폼을 통해 차트 인자를 설정
with st.sidebar.form(key='chartsetting', clear_on_submit=True):
    st.header('차트 설정')
    ''
    ''
    symbols = getSymbols()
    choices = zip(symbols.Code, symbols.Name, symbols.Market)
    choices = [ ' : '.join(x) for x in choices]
    # options에는 문자열, index에는 정수값
    choice = st.selectbox(label='종목:',options=choices, index=st.session_state['code_index'])
    code_index = choices.index(choice)
    code = choice.split()[0]
    ''
    ''
    ndays = st.slider(
        label='기간 (days)',
        min_value=5,
        max_value=365,
        value=st.session_state['ndays'],
        step=1
    )
    ''
    ''
    chart_styles = ['default','classic','binance','yahoo','brasil']
    chart_style = st.selectbox(label='차트 스타일', options=chart_styles, index=chart_styles.index(st.session_state['chart_style']))
    ''
    ''
    volume = st.checkbox('거래량',value=st.session_state['volume'])
    '---'

    if st.form_submit_button(label='OK'):
        st.session_state['ndays'] = ndays
        st.session_state['code_index'] = code_index
        st.session_state['chart_style'] = chart_style
        st.session_state['volume'] = volume
        st.experimental_rerun()


# 캔들차트를 출력
def plotChart(data):
    chart_style = 'default' # 'default', 'binance', 'classic', 'yahoo' 등 중에서 선택
    marketcolors = mpf.make_marketcolors(up='red', down='blue') 
    mpf_style = mpf.make_mpf_style(base_mpf_style = chart_style, marketcolors=marketcolors)

    fig, ax = mpf.plot(
        data = data,
        volume = False,
        type='candle',
        style= mpf_style,
        figsize=(10,7),
        fontscale = 1.1,
        mav = (5,10,30),                    # 이동평균선 (mav) 3개
        mavcolors=('red','green','blue'),
        returnfig = True                    # Figure 객체 반환
    )

    st.pyplot(fig)



# code에 해당하는 주식 데이터를 받아와서 출력해준다.
# code = '005930'   
# code = '373220'     

# date_start = (datetime.today() - timedelta(days=30)).date()
# date_end = datetime.today().date() # 년월일
# df = getData(code,date_start, date_end)
# plotChart(df)

date_start = (datetime.today()-timedelta(days=st.session_state['ndays'])).date()
date_end = datetime.today().date()
df = getData(code, date_start, date_end)     
chart_title = choices[st.session_state['code_index'] ]
st.markdown(f'<h3 style="text-align: center; color: black;">{chart_title}</h3>', unsafe_allow_html=True)
plotChart(df)

""
"-----"
""

stock_name = chart_title.split(":")[1].strip()
st.header("파일 내려받기")
st.dataframe(df)
# st.text(f'{stock_name}_{date_start}_{date_end}.csv')
st.download_button(label="파일 내려받기",data=df.to_csv(), file_name=f'{stock_name}_{date_start}_{date_end}.csv')

""
"-----"
""

st.header("파일 업로드")
myFile = st.file_uploader("CSV 파일 업로드") 
out1 = st.empty()

if myFile:
    out1.write('업로드 성공')
    myDF = pd.read_csv(myFile) # 올린 csv 파일을 pandas로 열여줘야함
    st.dataframe(myDF)