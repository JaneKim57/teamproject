import streamlit as st
import pandas as pd
import plotly.express as px

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
    # 파일 이름: 앱과 같은 폴더에 위치해야 함
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

    # 자치구 중심 위도/경도 (간단한 샘플)
    gu_center = {
        '종로구': [37.5729, 126.9794], '중구': [37.5636, 126.9972], '용산구': [37.5323, 126.9906],
        '성동구': [37.5633, 127.0364], '광진구': [37.5384, 127.0823], '동대문구': [37.5744, 127.0396],
        '중랑구': [37.6063, 127.0927], '성북구': [37.5894, 127.0167], '강북구': [37.6396, 127.0257],
        '도봉구': [37.6688, 127.0472], '노원구': [37.6554, 127.0775], '은평구': [37.6176, 126.9227],
        '서대문구': [37.5791, 126.9368], '마포구': [37.5663, 126.9014], '양천구': [37.5175, 126.8664],
        '강서구': [37.5509, 126.8495], '구로구': [37.4955, 126.8876], '금천구': [37.4569, 126.8958],
        '영등포구': [37.5264, 126.8963], '동작구': [37.5124, 126.9392], '관악구': [37.4784, 126.9516],
        '서초구': [37.4836, 127.0326], '강남구': [37.5172, 127.0473], '송파구': [37.5145, 127.1059],
        '강동구': [37.5302, 127.1238]
    }
    df['위도'] = df['자치구'].map(lambda x: gu_center.get(x, [None, None])[0])
    df['경도'] = df['자치구'].map(lambda x: gu_center.get(x, [None, None])[1])

    return df

df = load_and_merge_data()

# 사이드바 설정
st.sidebar.header("🔧 분석 조건 선택")
indicator = st.sidebar.selectbox("분석 지표", 
    ["자전거도로_길이", "자전거도로_밀도", "1인당_자전거도로", "인구밀도", "불균형_지수"])
selected_gu = st.sidebar.multiselect("자치구 필터", options=df['자치구'].unique(), default=df['자치구'].unique())

# 필터 적용
filtered_df = df[df['자치구'].isin(selected_gu)]

# 막대 그래프
st.subheader(f"📊 {indicator} 비교")
bar_fig = px.bar(filtered_df.sort_values(by=indicator, ascending=False),
                 x='자치구', y=indicator, color=indicator)
st.plotly_chart(bar_fig, use_container_width=True)

# 산점도
st.subheader("⚖️ 인구밀도 vs 자전거도로 밀도")
scatter_fig = px.scatter(filtered_df, x="인구밀도", y="자전거도로_밀도",
                         size="1인당_자전거도로", color="불균형_지수",
                         hover_name="자치구")
st.plotly_chart(scatter_fig, use_container_width=True)

# 지도
st.subheader(f"🗺️ 자치구 지도 시각화: {indicator}")
map_fig = px.scatter_mapbox(filtered_df, lat="위도", lon="경도", size=indicator,
                            color=indicator, hover_name="자치구",
                            mapbox_style="carto-positron", zoom=10, height=600)
st.plotly_chart(map_fig, use_container_width=True)
