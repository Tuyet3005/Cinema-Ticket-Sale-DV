import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title = "Doanh thu hang thang cua cac rap chieu phim", layout = 'wide', 
                   initial_sidebar_state = 'expanded')

#Read data from csv
data = pd.read_csv('datasets/data_preprocess.csv', index_col=0)

### Change type
data['date'] = pd.to_datetime(data['date'])
data[['film_code', 'cinema_code']] = data[['film_code', 'cinema_code']].astype(str)

### Side bar   
with st.sidebar:
    
    st.sidebar.subheader('Báo cáo tháng')
    month_filter = st.selectbox(label = 'Choose month', options = np.sort(data['month'].unique())[1:].tolist())
    month_df = data[data['month'] == month_filter]    
    
    st.sidebar.subheader('Top phim trong tháng')
    size = len(month_df['film_code'].unique())
    top_n_film = st.slider('Choose top film', 1, size, min(size, 5))
    
    st.sidebar.subheader('Top rạp trong tháng')
    size = len(month_df['cinema_code'].unique())
    top_n_cinema = st.slider('Choose top cinema', 1, size, min(size, 5))
    
    st.subheader('Độ cao hàng top doanh thu')
    plot1_height = st.sidebar.slider('Specify first row height', 350, 500, 400)
    
    st.sidebar.subheader('Donut Chart')
    size = len(month_df['film_code'].unique())
    n_film = st.slider('Choose num film', 1, size, min(size, 2))
    
    st.sidebar.subheader('Top rạp trong tháng')
    size = len(month_df['cinema_code'].unique())
    n_cinema =  st.slider('Choose num cinema', 1, size, min(size, 2))
    
    st.sidebar.subheader('Doanh thu theo ngày')
    chart1_type = st.selectbox(label = 'Choose type', options = ['scatter', 'line'])
    
    st.subheader('Độ cao hàng doanh thu theo ngày')
    plot2_height = st.sidebar.slider('Specify second row height', 350, 500, 400)
    
    
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

st.markdown(f'<h1 class="title">BÁO CÁO TỔNG THỂ THÁNG {month_filter}</h1>', unsafe_allow_html=True)
# st.title(f"BÁO CÁO RẠP PHIM THÁNG {month_filter}")

### Row 1
col1, col2, col3, col4 = st.columns([3.5, 1.5, 2, 2])

### First metric: Doanh thu
### Doanh thu:
total_profit = int(month_df['total_sales'].sum())
pre_total_profit = int(data[data['month'] == month_filter - 1]['total_sales'].sum())
raise_ = (total_profit - pre_total_profit) / pre_total_profit
with col1:
    st.metric("Tổng doanh thu", '{:,.0f}'.format(total_profit), str(round(raise_, 2)) + '%')

### Second metric: Thống kê số phim
total_film = len(month_df['film_code'].unique())
pre_total_film = len(data[data['month'] == month_filter - 1]['film_code'].unique())
raise_ = total_film - pre_total_film
with col2:
    st.metric("Tổng số phim", '{:,.0f}'.format(total_film), raise_)

### Third metric: Số xuất chiếu
total_showtime = len(month_df.index)
pre_total_showtime = len(data[data['month'] == month_filter - 1].index)
raise_ = total_showtime - pre_total_showtime
with col3:
    st.metric("Tổng số suất chiếu", '{:,.0f}'.format(total_showtime), raise_)


# Forth metric: Số vé bán được
total_tickets = int(month_df['tickets_sold'].sum())
pre_total_tickets = int(data[data['month'] == month_filter - 1]['tickets_sold'].sum())
raise_ = (total_tickets - pre_total_tickets) / pre_total_tickets
with col4:
    st.metric("Tổng số vé bán ra", '{:,.0f}'.format(total_tickets), str(round(raise_, 2)) + '%')


### Row 1
col1, col2 = st.columns((1, 1))

### First chart
sc1 = month_df.groupby('film_code')['total_sales'].sum().reset_index()
sc1 = sc1.sort_values('total_sales', ascending=False)
sc = sc1.head(top_n_film)

fig = px.bar(sc, x=range(top_n_film), y='total_sales')

fig.update_xaxes(
    tickmode='array',
    tickvals = list(range(top_n_film)),
    ticktext = sc['film_code']
)

fig.update_layout(
    xaxis_title = 'Mã phim',
    yaxis_title = 'Tổng doanh thu',
    height = plot1_height,
    title={
        'text': f'Top {top_n_film} phim có doanh thu cao nhất trong tháng',
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    }
)

with col1:
    st.plotly_chart(fig, use_container_width = True)
    
### Second chart
sc2 = month_df.groupby('cinema_code')['total_sales'].sum().reset_index()
sc2 = sc2.sort_values('total_sales', ascending=False)
sc = sc2.head(top_n_cinema)

fig = px.bar(sc, x=range(top_n_cinema), y='total_sales')

fig.update_xaxes(
    tickmode='array',
    tickvals = list(range(top_n_cinema)),
    ticktext = sc['cinema_code']
)

fig.update_layout(
    xaxis_title = 'Mã rạp',
    yaxis_title = 'Tổng doanh thu',
    height = plot1_height,
    title={
        'text': f'Top {top_n_cinema} rạp có doanh thu cao nhất trong tháng',
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    }
)

with col2:
    st.plotly_chart(fig, use_container_width = True)

### Row 2
col1, col2 = st.columns((1, 1))


temp = month_df.copy()
temp['weekday'] = data['date'].dt.day_name()
temp = temp.groupby([temp['date'].dt.day_of_week, temp['weekday']]).agg({'total_sales': 'mean'}).reset_index()
fig = px.bar(x = temp['weekday'], y = temp['total_sales'])
fig.update_layout(
    xaxis_title = 'Ngày trong tuần',
    yaxis_title = 'Doanh thu trung bình',
    height = plot2_height,
    title={
        'text': 'Doanh thu trung bình của các ngày trong tuần',
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    }
)

with col1:
    st.plotly_chart(fig, use_container_width = True)


def top_n_and_other(df, n):
    new_df = df.head(n).T
    new_df['new'] = pd.Series(['other'])
    new_df.at['total_sales', 'new'] = df.iloc[n:]['total_sales'].sum()
    try:
        new_df.at['film_code', 'new'] = 'other'
    except:
        new_df.at['cinema_code', 'new'] = 'other'
    return new_df.T
         

fig = go.Figure()

new_df_film = top_n_and_other(sc2, n_film)
fig.add_trace(go.Pie(labels = new_df_film['cinema_code'],
                             values = new_df_film['total_sales'],
                             hole = 0.4)
              )

new_df_cinema = top_n_and_other(sc1, n_cinema)
fig.add_trace(go.Pie(labels = new_df_cinema['film_code'],
                             values = new_df_cinema['total_sales'],
                             hole = 0.8)
              )

fig.update_layout(
    title={
        'text': 'Tỉ trọng doanh thu theo rạp và phim',
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    },
    showlegend=False
)

with col2:
    st.plotly_chart(fig, use_container_width = True)

### Row 3
col = st.columns((1))

# First plot
temp = month_df.groupby(['date']).agg({'total_sales': ['sum']}).sort_index().reset_index()
temp.columns = ['date', 'total_sales']
temp['date'] = pd.to_datetime(temp['date'])

if chart1_type == 'scatter':
    
    fig = px.scatter(temp, x = 'date', y = 'total_sales')
    
elif chart1_type == 'line':
    fig = px.line(temp, x = 'date', y = 'total_sales')
    
fig.update_layout(
    xaxis_title = 'Thời gian',
    yaxis_title = 'Tổng doanh thu',
    height = plot2_height,
    title={
        'text': 'Tổng doanh thu theo ngày',
        'x': 0.5,  # Giữa trục x
        'xanchor': 'center',  # Căn giữa theo trục x
        'yanchor': 'top'  # Căn theo trục y
    }
)

with col[0]:
    st.plotly_chart(fig, use_container_width = True)


