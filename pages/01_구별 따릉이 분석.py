import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    # CSV 파일 경로 (같은 디렉토리에 두세요)
    pop_file = "등록인구_동별(2024).csv"
    area_file = "행정구역_구별(2024).csv"
    bike_file = "자전거도로_현황(2024).csv"
    
    # 인구 데이터
    df_pop = pd.read_csv(pop_file, encoding='utf-8').iloc[1:].copy()
    df_pop.columns = ['자치구', '항목', '인구']
    df_pop = df_pop[df_pop['항목'] == '계']
    df_pop['인구'] = df_pop['인구'].astype(int)

    # 면적 데이터
    df_area = pd.read_csv(area_file, encoding='utf-8').iloc[2:].copy()
    df_area.columns = ['서울시', '자치구', '면적']
    df_area['면적'] = df_area['면적'].astype(float)

    # 자전거도로 데이터
    df_bike = pd.read_csv(bike_file, encoding='utf-8').iloc[2:].copy()
    df_bike.columns = ['합계', '구분', '자치구', '자전거도로_길이']
    df_bike['자전거도로_길이'] = df_bike['자전거도로_길이'].astype(float)

    # 병합
    df = pd.merge(df_pop[['자치구', '인구']], df_area[['자치구', '면적']], on='자치구')
    df = pd.merge(df, df_bike[['자치구', '자전거도로_길이']], on='자치구')

    # 지표 계산
    df['인구밀도'] = df['인구'] / df['면적']
    df['자전거도로_밀도'] = df['자전거도로_길이'] / df['면적']
    df['1인당_자전거도로'] = df['자전거도로_길이'] / df['인구']
    df['불균형_지수'] = df['인구밀도'] / df['자전거도로_밀도']

    return df

# 데이터 로드
df = load_data()

# 앱 UI
st.title("🚴 서울시 자전거도로 인프라 및 불균형 분석")
st.markdown("서울시 자치구별 인구, 면적, 자전거도로 데이터를 기반으로 다양한 인프라 지표를 분석합니다.")

# 지표 선택
indicator = st.selectbox("📊 시각화할 지표 선택", 
                         ["자전거도로_길이", "자전거도로_밀도", "1인당_자전거도로", "인구밀도", "불균형_지수"])

# Top N 슬라이더
top_n = st.slider("상위 자치구 수", min_value=5, max_value=25, value=10)

# 막대 그래프
sorted_df = df.sort_values(by=indicator, ascending=False).head(top_n)
bar_fig = px.bar(sorted_df, x='자치구', y=indicator, color=indicator,
                 title=f"{indicator} 기준 상위 {top_n} 자치구",
                 labels={'자치구': '자치구', indicator: indicator})

st.plotly_chart(bar_fig, use_container_width=True)

# 산점도
st.subheader("⚖️ 인구밀도 vs 자전거도로 밀도 비교")
scatter_fig = px.scatter(df,
                         x="인구밀도", y="자전거도로_밀도",
                         size="1인당_자전거도로", color="불균형_지수",
                         hover_name="자치구",
                         title="인구밀도 대비 자전거도로 밀도 (색: 불균형 지수, 크기: 1인당 도로길이)")
st.plotly_chart(scatter_fig, use_container_width=True)
