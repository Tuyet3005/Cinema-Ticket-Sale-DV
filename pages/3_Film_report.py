import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title = "Báo cáo doanh thu phim", layout = 'wide', 
                   initial_sidebar_state = 'expanded')

#Read data from csv
data = pd.read_csv('datasets/data_preprocess.csv', index_col=0)

### Change type
data['date'] = pd.to_datetime(data['date'])
data[['film_code', 'cinema_code', 'month']] = data[['film_code', 'cinema_code', 'month']].astype(str)
new_data = data.copy()
new_data['month'] = 'All time'
data = pd.concat([data, new_data], ignore_index=True)
### Side bar   
with st.sidebar:

    film_filter = st.selectbox(label = 'Chọn mã phim', options = np.sort(data['film_code'].unique())[:].tolist())
    film_df = data[data['film_code'] == film_filter]    

    list_month = film_df['month'].unique()
    list_month = np.sort(list_month[list_month != 'All time'].astype(int)).astype(str).tolist()
    list_month.insert(0, 'All time') ## Thêm All time vào đầu

    month_filter = st.selectbox(label='Chọn tháng', options=list_month)
    month_df = film_df[film_df['month'] == month_filter]    

    max_cinemas = len(month_df.groupby('cinema_code'))
    if max_cinemas > 20:
        max_cinemas = 20
    if max_cinemas < 10:
        cinema_filter = st.slider('Chọn số lượng rạp:', 0, max_cinemas, max_cinemas)
    else:
        cinema_filter = st.slider('Chọn số lượng rạp:', 0, max_cinemas, 10)
    
    top_cinema =  month_df.groupby('cinema_code')['tickets_sold'].sum().sort_values(ascending=False)
    
    
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

st.markdown(f'<h1 class="title">BÁO CÁO PHIM {film_filter}</h1>', unsafe_allow_html=True)
st.markdown("#")

def metric_rank():
    sales_by_film = data[data["month"] == month_filter].groupby("film_code")["total_sales"].sum().sort_values(ascending=False)
    film_rank = sales_by_film.index.get_loc(film_filter) + 1
    return film_rank

def metric_profit():
    total_profit = int(month_df['total_sales'].sum())
    if month_filter == 'All time':
        return total_profit, 0
    pre_total_profit = int(film_df[film_df['month'] == str(int(month_filter) - 1)]['total_sales'].sum())
    if pre_total_profit == 0:  
        raise_ = 0
    else: 
        raise_ = (total_profit - pre_total_profit) / pre_total_profit
    return total_profit, raise_

def metric_show_time():
    total_showtime = int(month_df['show_time'].sum())
    if month_filter == 'All time':
        return total_showtime, 0
    pre_total_showtime = int(film_df[film_df['month'] == str(int(month_filter) - 1)]['show_time'].sum())
    if pre_total_showtime == 0:
        raise_ = 0
    else:
        raise_ = total_showtime - pre_total_showtime
    return total_showtime, raise_

def metric_tickets():
    total_tickets = int(month_df['tickets_sold'].sum())
    if month_filter == 'All time':
        return total_tickets, 0
    pre_total_tickets = int(film_df[film_df['month'] == str(int(month_filter) - 1)]['tickets_sold'].sum())
    if pre_total_tickets == 0:
        raise_ = 0
    else:
        raise_ = (total_tickets - pre_total_tickets) / pre_total_tickets
    return total_tickets, raise_

def set_title(fig, x_title, y_title, chart_title):
    fig.update_layout(
    xaxis_title = x_title,
    yaxis_title = y_title,
    title={
        'text': chart_title,
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    }
    )
    return fig



def daily_sales_chart(type):
    sales_by_day = month_df.groupby('date')['total_sales'].sum()
    if type == 'line':
        fig = px.line(sales_by_day, x = sales_by_day.index, y = sales_by_day.values)
    elif type =='scatter':
        fig = px.scatter(sales_by_day, x = sales_by_day.index, y = sales_by_day.values)
    elif type =='bar':
        fig = px.bar(sales_by_day, x = sales_by_day.index, y = sales_by_day.values)
    fig = set_title(fig, "Ngày", "Doanh thu", "Doanh thu các ngày trong tháng")
    return fig

def daily_tickets_chart(type):
    tickets_by_day = month_df.groupby('date')['tickets_sold'].sum()
    if type =='line':
        fig = px.line(tickets_by_day, x = tickets_by_day.index, y = tickets_by_day.values)
    elif type == 'scatter':
        fig = px.scatter(tickets_by_day, x = tickets_by_day.index, y = tickets_by_day.values)
    elif type =='bar':
        fig = px.bar(tickets_by_day, x = tickets_by_day.index, y = tickets_by_day.values)
    fig = set_title(fig, "Ngày", "Số vé bán", "Số vé bán các ngày trong tháng")
    return fig
def daily_show_time_chart(type):
    show_time_by_day = month_df.groupby('date')['show_time'].sum()
    if type == 'line':
        fig = px.line(show_time_by_day, x = show_time_by_day.index, y = show_time_by_day.values)
    elif type =='scatter':
        fig = px.scatter(show_time_by_day, x = show_time_by_day.index, y = show_time_by_day.values)
    elif type =='bar':
        fig = px.bar(show_time_by_day, x = show_time_by_day.index, y = show_time_by_day.values)
    fig = set_title(fig, "Ngày", "Số suất chiếu", "Số suất chiếu các ngày trong tháng")
    return fig

def ticket_price_chart():
    bins = [0, 50000, 80000, 100000, 120000, float('inf')]

    # Chia cột "ticket_price" thành bins
    month_df['price_bin'] = pd.cut(month_df['ticket_price'], bins=bins, labels=False, right=False)

    # Đổi tên các bins thành các giá trị tương ứng
    bin_labels = ['price <= 50000', '50000 < price <= 80000', '80000 < price <= 100000', '100000 < price <= 120000', 'price > 120000']
    month_df['price_bin'] = month_df['price_bin'].replace(range(len(bin_labels)), bin_labels)

    # Tính tổng số lượng phần tử trong mỗi bin
    bin_counts = month_df['price_bin'].value_counts().reset_index()
    fig = go.Figure(data=go.Pie(labels=bin_counts['index'], values=bin_counts['price_bin'], hole=0.4))
    fig.update_layout(
        title={
            'text': 'Phân bố giá vé tại các rạp',
            'x': 0.5,  # Giữa trục x
            'xanchor': 'center',  # Căn giữa theo trục x
            'yanchor': 'top'  # Căn theo trục y
        }
    )

    return fig, bin_labels

def tickets_sold_by_price_chart(bin_labels):
    month_df['price_bin'] = pd.Categorical(month_df['price_bin'], categories=bin_labels, ordered=True)

    tickets_by_price = month_df.groupby('price_bin')['tickets_sold'].sum().reset_index()

    fig = px.bar(tickets_by_price, x='price_bin', y='tickets_sold', title='Phân bố số lượng vé bán ra theo giá vé')
    fig = set_title(fig, "Giá vé", "Số vé bán", "Số vé bán theo giá vé")
    return fig


def tickets_sold_by_cinema_chart():

    top_x_cinema = top_cinema.iloc[:cinema_filter].sort_values()

    fig = px.bar(top_x_cinema, x=top_x_cinema.values, y=top_x_cinema.index, orientation='h')
    fig = set_title(fig, "Số vé bán", "Mã rạp phim", "Số vé bán ở các rạp phim")
    fig.update_layout(yaxis={'type': 'category'})
    return fig, top_x_cinema

def occu_perc_by_cinema_chart(top_x_cinema):
    cinema_df = month_df[month_df['cinema_code'].isin(top_x_cinema.index)]
    cinema_df = cinema_df.groupby(["cinema_code", "date"])["occu_perc"].mean().unstack(level="date")

    fig = go.Figure(data=go.Heatmap(
            z=cinema_df.values,
            x=cinema_df.columns,
            y=cinema_df.index,
            colorscale='Blues'
    ))
    fig = set_title(fig, "Ngày", "Mã rạp phim", "Tỷ  lệ chiếm chỗ ở các rạp")
    fig.update_layout(yaxis={'type': 'category'})
    return fig

############################===========DRAW DASHBOARD=============================#############################


###========================= Merics rows

col1, col2, col3, col4 = st.columns([2, 4, 3, 2])

film_rank = metric_rank()
total_profit, raise_profit = metric_profit()
total_showtime, raise_show_time = metric_show_time()
total_tickets, raise_tickets = metric_tickets()
### First metrict: Rank
with col1:
    st.metric("Rank", '#{:,.0f}'.format(film_rank))

### Second metric: Doanh thu

with col2:
    st.metric("Tổng doanh thu", '{:,.0f}'.format(total_profit), str(round(raise_profit, 2)) + '%')

### Third metric: Số xuất chiếu

with col3:
    st.metric("Tổng số suất chiếu", '{:,.0f}'.format(total_showtime), raise_show_time)


### Forth metric: Số vé bán được

with col4:
    st.metric("Tổng số vé bán ra", '{:,.0f}'.format(total_tickets), str(round(raise_tickets, 2)) + '%')

###================= Row 1
tab1, tab2, tab3 = st.tabs(["Bar", "Line", "Scatter"])

with tab1:
    fig = daily_sales_chart('bar')
    st.plotly_chart(fig, use_container_width = True)
with tab2:
    fig = daily_sales_chart('line')
    st.plotly_chart(fig, use_container_width = True)
with tab3:
    fig = daily_sales_chart('scatter')
    st.plotly_chart(fig, use_container_width = True)
####================= Row 2:
col1, col2 = st.columns([5, 5])

with col1:
    tab1, tab2, tab3 = st.tabs(["Bar", "Line", "Scatter"])
    with tab1:
        fig1 = daily_tickets_chart('bar')
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig1 = daily_tickets_chart('line')
        st.plotly_chart(fig1, use_container_width=True)      
    with tab3:
        fig1 = daily_tickets_chart('scatter')
        st.plotly_chart(fig1, use_container_width=True)     

with col2:
    tab1, tab2, tab3 = st.tabs(["Bar", "Line", "Scatter"])
    with tab1:
        fig1 = daily_show_time_chart('bar')
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig1 = daily_show_time_chart('line')
        st.plotly_chart(fig1, use_container_width=True)      
    with tab3:
        fig1 = daily_show_time_chart('scatter')
        st.plotly_chart(fig1, use_container_width=True)     

####===================== Row 3
col1, col2 = st.columns((3.5, 6.5))

fig1, bin_labels = ticket_price_chart()
fig2 = tickets_sold_by_price_chart(bin_labels)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

##========================== Row 4:
col1, col2 = st.columns((3, 1))
fig2, top_x_cinema = tickets_sold_by_cinema_chart()
fig1 = occu_perc_by_cinema_chart(top_x_cinema)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)



