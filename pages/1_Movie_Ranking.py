import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def total_sales_ranking(df, month, asc=True):
    prev_data = df[df['month'] == month-1].groupby(['film_code']).agg(
        {'total_sales': 'sum'}).reset_index()
    prev_data['rank'] = prev_data['total_sales'].rank(ascending=False)

    data = df[df['month'] == month].groupby(['film_code']).agg(
        {'total_sales': 'sum'}).reset_index()
    data['rank'] = data['total_sales'].rank(ascending=False)
    data = data.sort_values(by='total_sales', ascending=asc)

    fig = px.bar(data, x='total_sales', y='film_code',
                height=1000,
                title=f"Xếp hạng phim theo tổng doanh thu (tháng {month})",
                labels={"total_sales": "Tổng doanh thu", "film_code": "Mã phim"},
                orientation='h',)
    fig.update_yaxes(type='category')

    data = data.merge(prev_data, on='film_code', how='left')
    data['value'] = data['total_sales_x']
    data['delta_ranking'] = np.where(data['rank_y'].notnull(), data['rank_y'] - data['rank_x'], 0)
    data['delta_value'] = np.where(data['total_sales_y'].notnull(), data['total_sales_y'] - data['total_sales_x'], 0)

    return fig, data

def tickets_sold_ranking(df, month, asc=True):
    prev_data = df[df['month'] == month-1].groupby(['film_code']).agg(
        {'tickets_sold': 'sum'}).reset_index()
    prev_data['rank'] = prev_data['tickets_sold'].rank(ascending=False)

    data = df[df['month'] == month].groupby(['film_code']).agg(
        {'tickets_sold': 'sum'}).reset_index()
    data['rank'] = data['tickets_sold'].rank(ascending=False)
    data = data.sort_values(by='tickets_sold', ascending=asc)

    fig = px.bar(data, x='tickets_sold', y='film_code',
                height=1000,
                title=f"Xếp hạng phim theo số lượng vé bán ra (tháng {month})",
                labels={"tickets_sold": "Số lượng vé bán ra", "film_code": "Mã phim"},
                orientation='h',)
    fig.update_yaxes(type='category')

    data = data.merge(prev_data, on='film_code', how='left')
    data['value'] = data['tickets_sold_x']
    data['delta_ranking'] = np.where(data['rank_y'].notnull(), data['rank_y'] - data['rank_x'], 0)
    data['delta_value'] = np.where(data['tickets_sold_y'].notnull(), data['tickets_sold_y'] - data['tickets_sold_x'], 0)

    return fig, data

def tickets_out_percent_ranking(df, month, asc=True):
    prev_data = df[df['month'] == month-1].groupby(['film_code']).agg(
        {'tickets_out': 'sum', 'tickets_sold': 'sum'})
    prev_data['tickets_out_percent'] =(prev_data['tickets_out'] / prev_data['tickets_sold']) * 100
    prev_data['rank'] = prev_data['tickets_out_percent'].rank(ascending=False)

    data = df[df['month'] == month].groupby(['film_code']).agg(
        {'tickets_out': 'sum', 'tickets_sold': 'sum'})
    data['tickets_out_percent'] = (data['tickets_out'] / data['tickets_sold']) * 100
    data['rank'] = data['tickets_out_percent'].rank(ascending=False)
    data = data.reset_index().sort_values(by='tickets_out_percent', ascending=asc)

    fig = px.bar(data, x='tickets_out_percent', y='film_code',
                height=1000,
                title=f"Xếp hạng phim theo tỉ lệ hủy vé (tháng {month})",
                labels={"tickets_out_percent": "Tỉ lệ hủy vé (%)", "film_code": "Mã phim"},
                orientation='h',)
    fig.update_yaxes(type='category')

    data = data.merge(prev_data, on='film_code', how='left')
    data['value'] = data['tickets_out_percent_x']
    data['delta_ranking'] = np.where(data['rank_y'].notnull(), data['rank_y'] - data['rank_x'], 0)
    data['delta_value'] = np.where(data['tickets_out_percent_y'].notnull(), data['tickets_out_percent_y'] - data['tickets_out_percent_x'], 0)

    return fig, data

def movie_chart(df, film_code):
    data = df[df['film_code'] == film_code]
    data = data.groupby(['month']).agg(
        {'total_sales': 'sum', 'ticket_price': 'mean', 'tickets_sold': 'sum'}).reset_index()

    fig = make_subplots(rows=3, cols=1, x_title='Tháng', vertical_spacing = 0.1)

    fig.add_trace(go.Scatter(x=data.month, y=data.total_sales, name='Doanh thu'),
                1, 1)
    fig.add_trace(go.Scatter(x=data.month, y=data.tickets_sold, name='Số lượng vé đã bán'),
                2, 1)
    fig.add_trace(go.Scatter(x=data.month, y=data.ticket_price, name='Giá vé'),
                3, 1)

    fig['layout']['yaxis']['title']='Doanh thu'
    fig['layout']['yaxis2']['title']='Số lượng vé đã bán'
    fig['layout']['yaxis3']['title']='Giá vé'

    fig.update_layout(height=800,
                    title_text=f"Các biến động của phim {film_code} theo thời gian")

    return fig

#Read data from csv
df = pd.read_csv('datasets/data_preprocess.csv', index_col=0)

st.set_page_config(
    page_title = 'Bảng xếp hạng phim',
    layout = 'wide'
)
st.sidebar.markdown("Dashboard giúp người dùng xem bảng xếp hạng phim theo nhiều yếu tố khác nhau")

#Dashboard title
st.title("Bảng xếp hạng phim")

#Filter
ranking_by_filter = st.sidebar.selectbox("Xếp hạng theo", pd.Series(["Tổng doanh thu", "Số lượng vé bán ra", "Tỉ lệ hủy vé"]))
order_by_filter = st.sidebar.selectbox("Thứ tự", pd.Series(["Tăng dần", "Giảm dần"]))
month_filter = st.sidebar.slider('Thời gian (3/2018 - 11/2018)', 3, 11, 3)

if ranking_by_filter == 'Tổng doanh thu':
    fig, data = total_sales_ranking(df, month_filter, asc=order_by_filter=='Tăng dần')
elif ranking_by_filter == 'Số lượng vé bán ra':
    fig, data = tickets_sold_ranking(df, month_filter, asc=order_by_filter=='Tăng dần')
elif ranking_by_filter == 'Tỉ lệ hủy vé':
    fig, data = tickets_out_percent_ranking(df, month_filter, asc=order_by_filter=='Tăng dần')

default_color = "blue"
colors = {"China": "red"}
color_discrete_map = {
    c: colors.get(c, default_color) 
    for c in data['film_code']}

selected_movie_code = None

fig_col1, fig_col2 = st.columns(2)
with fig_col2:
    movie_filter = st.selectbox("Chọn mã phim", data['film_code'][::-1])

    selected_movie_code = movie_filter

    selected_movie = data[data['film_code']==selected_movie_code]
    mettric1, mettric2 = st.columns([1,3])
    mettric1.metric(label="Xếp hạng", value=int(selected_movie['rank_x'].values[0]), 
                    delta=int(selected_movie['delta_ranking'].values[0]))
    mettric2.metric(label=ranking_by_filter, value='{:20,.2f}'.format(selected_movie['value'].values[0]), 
                    delta='{:20,.2f}'.format(selected_movie['delta_value'].values[0]))
    
    fig1 = movie_chart(df.reset_index(), selected_movie_code)

    st.plotly_chart(fig1, use_container_width=True)

with fig_col1:
    fig["data"][0]["marker"]["color"] = ["#FB8090" if c == selected_movie_code
                                         else "#83C9FF" for c in fig["data"][0]["y"]]

    st.plotly_chart(fig, use_container_width=True)
