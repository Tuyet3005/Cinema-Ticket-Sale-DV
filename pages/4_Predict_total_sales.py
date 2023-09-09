import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA
import datetime 
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title = "Dự đoán doanh thu", layout = 'wide', 
                   initial_sidebar_state = 'expanded')

#Read data from csv
data = pd.read_csv('datasets/data_preprocess.csv', index_col=0)

### Change type
data['date'] = pd.to_datetime(data['date'])
data[['film_code', 'cinema_code']] = data[['film_code', 'cinema_code']].astype(str)

### Side bar   
with st.sidebar:
    st.subheader('Chọn ngày cuối cùng')
    data['date'] = pd.to_datetime(data['date'])
    start_date = data['date'].min().to_pydatetime()
    end_date = data['date'].max().to_pydatetime()
    to = st.slider('Choose end date for train', start_date, end_date, value = end_date)
    
    st.subheader('Số ngày muốn dự đoán')
    num_day = st.sidebar.slider('Choose num of day', 5, 10, 15)
    
### Title
st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
### Row 4
st.markdown(f'<h1 class="title">Mô hình ARIMA dự đoán doanh thu</h1>', unsafe_allow_html=True)

### Row 5
col1, col2 = st.columns((3, 1))

### ARIMA
temp = data[data['date'] <= to]
train = temp[['date', 'total_sales']]
train = train.groupby(['date'])['total_sales'].sum()
train.columns = ['total_sales']
fill_data = pd.DataFrame(index = ['total_sales'])

i = train.index[0]
while i <= to:
    if i not in train.index:
        prev = i - pd.DateOffset(days=1)
        while prev not in train.index:
            prev = prev - pd.DateOffset(days=1)
            
        next_ = i + pd.DateOffset(days=1)
        while next_ not in train.index:
            next_ = next_ + pd.DateOffset(days=1)
        
        val = (train.loc[prev] * (next_ - i).days + train.loc[next_] * (i - prev).days) / (next_ - prev).days
        fill_data[i.strftime('%Y-%m-%d')] = round(val)
    i += pd.DateOffset(days=1)
fill_data = fill_data.T
train = pd.concat([train, fill_data])
train.index = pd.to_datetime(train.index)
train['total_sales'] = train['total_sales'].fillna(train[0])
train = train.drop(0, axis=1)
train = train.sort_index()

model = ARIMA(train['total_sales'], order=(3, 1, 2))
model_fit = model.fit()

from_ = train.index[-1]
to_ =  train.index[-1] + pd.DateOffset(days = num_day)
predictions = model_fit.predict(start = from_, end = to_)

fig = go.Figure()
fig.add_trace(go.Scatter(x = train.index, y = train['total_sales'], name='Train data', mode = 'lines'))
fig.add_trace(go.Scatter(x = predictions.index, y = predictions.values, name = 'Prediction', mode = 'lines', line=dict(color='red')))

fig.update_layout(
    xaxis_title = 'Thời gian',
    yaxis_title = 'Tổng doanh thu',
    title={
        'text': f"Dự đoán doanh thu từ {from_.strftime('%Y-%m-%d')} đến {to_.strftime('%Y-%m-%d')}",
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    },
    legend=dict(
        x = 0.9,  # Vị trí ngang, giữa trục x
        y = 1.1,  # Vị trí dọc, ở trên cùng
        xanchor='center',  # Căn giữa theo trục x
        yanchor='top'  # Căn theo trục y
    )
)

with col1:
    st.plotly_chart(fig, use_container_width = True)
    
with col2:
    st.dataframe(predictions)
    
