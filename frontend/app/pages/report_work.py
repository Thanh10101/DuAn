import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title='Báo cáo công việc', layout='wide')

COLUMNS = [
    'mô tả công việc',
    'thời gian bắt đầu',
    'thời gian kết thúc',
    'tồn động',
    'loại công việc'
]


def load_data(uploaded_file=None):
    if uploaded_file:
        return pd.read_excel(uploaded_file)
    return pd.DataFrame(columns=COLUMNS)


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


st.title('📊 Báo cáo công việc')

uploaded_file = st.sidebar.file_uploader(
    'Import file Excel',
    type=['xlsx']
)

df = load_data(uploaded_file)

st.subheader('Dữ liệu công việc')
editable_df = st.data_editor(
    df,
    num_rows='dynamic',
    width="stretch"
)

if not editable_df.empty:

    # convert datethời gian làm việc
    editable_df['thời gian bắt đầu'] = pd.to_datetime(
        editable_df['thời gian bắt đầu'],
        errors='coerce'
    )

    editable_df['thời gian kết thúc'] = pd.to_datetime(
        editable_df['thời gian kết thúc'],
        errors='coerce'
    )

    # tính thời gian công việc
    editable_df['time'] = (
        editable_df['thời gian kết thúc']
        - editable_df['thời gian bắt đầu']
    )

    # tổng thời gian
    tong = editable_df['time'].sum()

    st.metric(
        "Tổng thời gian làm việc",
        str(tong)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Thống kê theo ngày')

        daily = (
            editable_df
            .groupby(editable_df['thời gian bắt đầu'])
            .size()
            .reset_index(name='Số công việc')
        )

        fig1 = px.bar(
            daily,
            x='thời gian bắt đầu',
            y='Số công việc'
        )

        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader('Thống kê theo tháng')

        editable_df['tháng'] = editable_df[
            'thời gian bắt đầu'
        ].dt.to_period('M').astype(str)

        monthly = (
            editable_df
            .groupby('tháng')
            .size()
            .reset_index(name='Số công việc')
        )

        fig2 = px.line(
            monthly,
            x='tháng',
            y='Số công việc',
            markers=True
        )

        st.plotly_chart(fig2, width="stretch")

    st.subheader('Thống kê loại công việc')

    type_count = (
        editable_df
        .groupby('loại công việc')
        .size()
        .reset_index(name='Số lượng')
    )

    fig3 = px.pie(
        type_count,
        names='loại công việc',
        values='Số lượng'
    )

    st.plotly_chart(fig3, width="stretch")

# export
excel_data = to_excel(editable_df)

st.download_button(
    label='📥 Export Excel',
    data=excel_data,
    file_name=f'bao_cao_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

st.sidebar.info(
    'Chạy bằng lệnh:\nstreamlit run bao_cao_cong_viec.py'
)