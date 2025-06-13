import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import json

# 페이지 설정
st.set_page_config(page_title="서울시 자전거도로 분석", layout="wide")

# 메인 소개
st.title("🚴 서울시 자전거도로 인프라 및 불균형 분석 대시보드")
st.markdown("""
---
### 📌 프로젝트 개요
서울시 **자치구별 인구**, **면적**, **자전거도로 길이** 데이터를 바탕으로 다음과 같은 분석을 수행합니다:

1. 자전거도로 인프라 밀도 분석  
2. 인구 대비 자전거도로 불균형 지수 도출  
   (불균형 지수 = 인구밀도 / 자전거도로 밀도)

---
### 🧭 사용 방법
- 왼쪽에서 지표와 자치구를 선택하세요.
- 아래 시각화에서 분석 결과를 확인할 수 있습니다.
---
""")

@st.cache_data
def load_and_merge_data():
    df_pop = pd.read_csv("등록인구_동별(2024).csv", encoding='utf-8').iloc[1:].copy()
    df_pop.columns = ['자치구', '항목', '인구']
    df_pop = df_pop[df_pop['항목'] == '계']
    df_pop['인구'] = df_pop['인구'].astype(int)

    df_area = pd.read_csv("행정구역_구별(2024).csv", encoding='utf-8').iloc[2:].copy()
    df_area.columns = ['서울시', '자치구', '면적']
    df_area['면적'] = df_area['면적'].astype(float)

    df_bike = pd.read_csv("자전거도로_현황(2024).csv", encoding='utf-8').iloc[2:].copy()
    df_bike.columns = ['합계', '구분', '자치구', '자전거도로_길이']
    df_bike['자전거도로_길이'] = df_bike['자전거도로_길이'].astype(float)

    df = pd.merge(df_pop[['자치구', '인구']], df_area[['자치구', '면적']], on='자치구')
    df = pd.merge(df, df_bike[['자치구', '자전거도로_길이']], on='자치구')

    df['인구밀도'] = df['인구'] / df['면적']
    df['자전거도로_밀도'] = df['자전거도로_길이'] / df['면적']
    df['1인당_자전거도로'] = df['자전거도로_길이'] / df['인구']
    df['불균형_지수'] = df['인구밀도'] / df['자전거도로_밀도']

    return df

df = load_and_merge_data()

# 사이드바
st.sidebar.header("🔧 분석 조건 선택")
indicator = st.sidebar.selectbox("분석 지표", 
    ["자전거도로_길이", "자전거도로_밀도", "1인당_자전거도로", "인구밀도", "불균형_지수"])
selected_gu = st.sidebar.multiselect("자치구 필터", options=df['자치구'].unique(), default=df['자치구'].unique())
filtered_df = df[df['자치구'].isin(selected_gu)]

# 📊 막대 그래프
st.subheader(f"📊 {indicator} 기준 자치구별 비교")
bar_fig = px.bar(filtered_df.sort_values(by=indicator, ascending=False),
                 x='자치구', y=indicator, color=indicator)
st.plotly_chart(bar_fig, use_container_width=True)

# ⚖️ 산점도
st.subheader("⚖️ 인구밀도 vs 자전거도로 밀도")
scatter_fig = px.scatter(filtered_df, x="인구밀도", y="자전거도로_밀도",
                         size="1인당_자전거도로", color="불균형_지수",
                         hover_name="자치구")
st.plotly_chart(scatter_fig, use_container_width=True)

# 🗺️ 지도 시각화 (Folium Choropleth)
st.subheader(f"🗺️ 자치구 지도 시각화 (Folium): {indicator}")

@st.cache_data
def load_geojson():
    with open("hangjeongdong_서울특별시.geojson", encoding='utf-8') as f:
        return json.load(f)

geojson = load_geojson()

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="cartodbpositron")

# Choropleth 계층
folium.Choropleth(
    geo_data=geojson,
    name="choropleth",
    data=df,
    columns=["자치구", indicator],
    key_on="feature.properties.sggnm",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=indicator
).add_to(m)

# 🔍 자치구 이름 툴팁 추가
folium.GeoJson(
    geojson,
    name="자치구 이름",
    tooltip=folium.GeoJsonTooltip(fields=["sggnm"], aliases=["자치구:"])
).add_to(m)

# 지도 출력
st_folium(m, width=800, height=600)
