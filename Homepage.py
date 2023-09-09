import streamlit as st
import pandas as pd

st.set_page_config(
    page_title = 'Giới thiệu',
    layout = 'wide',

)
st.sidebar.markdown("Giới thiệu")

st.title("Lab 3 môn Trực quan hóa dữ liệu - Dùng công cụ hoặc thư viện làm dashboard")

st.markdown("## Thông tin về bộ dữ liệu")
st.markdown("- Bộ dữ liệu cung cấp thông tin chi tiết về lịch sử bán vé của các rạp phim đối với từng phim trong năm 2018. Các thông tin liên quan đến rạp phim và tên phim được mã hóa.")
st.markdown("- Nguồn: https://www.kaggle.com/datasets/arashnic/cinema-ticket")
st.markdown("## Ý nghĩa của từng cột")

data = pd.read_csv(r"datasets/cinemaTicket_Ref.csv")
mean_col = pd.read_csv(r"datasets/columns_meaning.csv", index_col = 0)
mean_col['type'] = data.dtypes.to_list()
st.dataframe(mean_col)

