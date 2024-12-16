import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 데이터 로드 함수
@st.cache_data
def load_movie_data():
    # GeoJSON 파일 로드
    with open("gdf_korea_sido_2023.json", encoding="utf-8") as f:
        geojson = json.load(f)
    # 영화 데이터 로드
    movies = pd.read_csv("movies.csv", encoding="utf-8", skiprows=5)
    # 열 이름 정리
    movies.columns = ["지역", "한국영화_상영편수", "한국영화_매출액", "한국영화_관객수", "한국영화_점유율",
                      "외국영화_상영편수", "외국영화_매출액", "외국영화_관객수", "외국영화_점유율",
                      "전체_상영편수", "전체_매출액", "전체_관객수", "전체_점유율"]
    # 불필요한 행 제거
    movies = movies[movies["지역"].notna()]  # 지역 값이 없는 행 제거
    movies = movies[movies["지역"] != "합계"]  # "합계" 행 제거
    # 숫자 데이터 변환
    movies["전체_관객수"] = movies["전체_관객수"].str.replace(",", "").astype(int)
    # 필요한 열만 추출
    movies_cleaned = movies[["지역", "전체_관객수"]]
    return geojson, movies_cleaned

# 데이터 불러오기
geojson, movies = load_movie_data()

# Streamlit UI 설정
st.set_page_config(page_title="시도별 영화 관객수 시각화",  page_icon="🎥", layout="wide")
st.title("🎥 시도별 영화 관객수 비율")

st.markdown("""
**전국 시도별 영화관 이용자 비율을 지도 및 산점도 그래프로 시각화합니다.**  
아래 버튼을 눌러 **지도 시각화**와 **막대그래프**를 번갈아 가며 확인할 수 있습니다.
""")


# 버튼 상태 관리
if "view_option" not in st.session_state:
    st.session_state.view_option = "지도"

# 버튼 생성 - 너비를 꽉 채움
col1, col2 = st.columns(2)
with col1:
    if st.button("🗺️ 지도 시각화 보기", use_container_width=True):
        st.session_state.view_option = "지도"
with col2:
    if st.button("📊 막대그래프 보기", use_container_width=True):
        st.session_state.view_option = "막대그래프"

# 시각화 - 지도
if st.session_state.view_option == "지도":
    st.subheader("🗺️ 시도별 영화 관객수 지도")
    fig_movie = px.choropleth_mapbox(
        movies,
        geojson=geojson,
        featureidkey="properties.CTP_KOR_NM",  # GeoJSON의 지역명 키
        locations="지역",                     # 영화 데이터의 지역 컬럼
        color="전체_관객수",                   # 색상 기준 값
        color_continuous_scale="YlOrRd",
        mapbox_style="carto-positron",
        center={"lat": 36.5, "lon": 127.5},   # 대한민국 중심 좌표
        zoom=6,
        title="시도별 영화 관객수"
    )
    st.plotly_chart(fig_movie, use_container_width=True)

# 시각화 - 막대그래프
elif st.session_state.view_option == "막대그래프":
    st.subheader("📊 시도별 영화 관객수 막대그래프")
    fig_bar = px.bar(
        movies,
        x="지역",
        y="전체_관객수",
        title="시도별 영화 관객수 막대그래프",
        labels={"전체_관객수": "관객수", "지역": "지역"},
        color="전체_관객수",
        color_continuous_scale="YlOrRd"
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
