import streamlit as st
import pandas as pd
import plotly.express as px

# 제목
st.title("서울시 자치구별 자전거도로 밀도 시각화")

# 데이터 불러오기 (실제 앱 배포 시 CSV 파일로 대체 가능)
data = pd.DataFrame({
    '구': ['강남구', '강동구', '강북구', '강서구', '관악구'],  # 예시 구 일부
    '자전거도로_길이_km': [114.0, 76.6, 8.7, 77.6, 27.7],
    '면적': [79.01, 49.18, 47.20, 82.89, 59.14],
})
data['자전거도로_밀도(km/km²)'] = data['자전거도로_길이_km'] / data['면적']

# 자치구 선택 옵션
selected_gu = st.multiselect(
    "자치구 선택",
    options=data['구'].unique(),
    default=data['구'].unique()
)

# 선택된 자치구만 필터링
data_filtered = data[data['구'].isin(selected_gu)]

# Plotly bar chart
fig = px.bar(
    data_filtered,
    x='구',
    y='자전거도로_밀도(km/km²)',
    title='자치구별 자전거도로 밀도 (km/km²)',
    labels={'자전거도로_밀도(km/km²)': '자전거도로 밀도 (km/km²)'},
    text='자전거도로_밀도(km/km²)'
)
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

st.plotly_chart(fig)

# 데이터 테이블 표시
st.subheader("자치구별 자전거도로 밀도 데이터")
st.dataframe(data_filtered.reset_index(drop=True))

