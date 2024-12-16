import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 페이지 설정
st.set_page_config(
    page_title="대한민국 인구 통계 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 및 전체 스타일 설정
st.markdown("""
<style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fc;
            border-right: 1px solid #ddd;
            padding-top: 20px;
        }
        .title {
            font-size: 50px;
            font-weight: bold;
            color: #333333;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 20px;
            color: #555555;
            text-align: center;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 타이틀
st.markdown('<div class="title">📊 대한민국 인구 통계 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">성별 및 연령대별 인구 수를 지도와 테이블로 분석합니다.</div>', unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    population_data = pd.read_csv("2023_pop.csv", encoding="utf-8")
    with open("gdf_korea_sido_2023.json", encoding="utf-8") as f:
        geojson = json.load(f)
    return population_data, geojson

@st.cache_data
def load_movie_data():
    movies = pd.read_csv("movies.csv", encoding="utf-8", skiprows=5)
    movies.columns = ["지역", "한국영화_상영편수", "한국영화_매출액", "한국영화_관객수", "한국영화_점유율",
                      "외국영화_상영편수", "외국영화_매출액", "외국영화_관객수", "외국영화_점유율",
                      "전체_상영편수", "전체_매출액", "전체_관객수", "전체_점유율"]
    movies = movies[movies["지역"].notna() & (movies["지역"] != "합계")]
    movies["전체_관객수"] = movies["전체_관객수"].str.replace(",", "").astype(int)
    return movies[["지역", "전체_관객수"]]

@st.cache_data
def load_library_data():
    library_data = pd.DataFrame({
        "지역": ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
                "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도",
                "경상남도", "제주특별자치도"],
        "거주비율": [96.8, 100, 100, 89.6, 100, 96.1, 100, 100, 85.6, 96.2, 97.3, 91.3, 95.7, 89.5, 87.2, 100, 100]
    })
    return library_data

# 데이터 로드
population_data, geojson = load_data()

# 데이터 정제: 공백 제거 및 매칭 확인
population_data["행정구역"] = population_data["행정구역"].str.strip()
geo_regions = [feature["properties"]["CTP_KOR_NM"] for feature in geojson["features"]]
population_data = population_data[population_data["행정구역"].isin(geo_regions)]

# --- 사이드바 메뉴 ---
st.sidebar.header("📂 탐색 메뉴")
menu_option = st.sidebar.radio(
    "🔍 메뉴 선택",
    ["📊 대시보드", "🎥 영화 데이터", "📚 도서관"]
)

# --- 메인 콘텐츠 ---
if menu_option == "📊 대시보드":
    st.sidebar.header("📁 필터 옵션")
    selected_age_group = st.sidebar.selectbox(
        "연령대 선택",
        ["0~9세", "10~19세", "20~29세", "30~39세", "40~49세", "50~59세", "60~69세", "70~79세", "80~89세", "90~99세", "100세 이상"]
    )

    gender_option = st.sidebar.radio(
        "성별 선택",
        ["남", "여"]
    )

    # 컬럼 매칭
    column_mapping = {
        "남": f"2023년_남_{selected_age_group}",
        "여": f"2023년_여_{selected_age_group}"
    }
    selected_column = column_mapping[gender_option]

    # 데이터 컬럼 확인 및 선택
    if selected_column in population_data.columns:
        population_selected = population_data[["행정구역", selected_column]]
        population_selected = population_selected.rename(columns={selected_column: "인구 수"})

        # 지도와 테이블을 나란히 배치
        col1, col2 = st.columns([2, 1])  # 비율 2:1로 설정

        with col1:
            st.subheader(f"📍 {selected_age_group} ({gender_option}) 인구 분포 지도")
            map_fig = px.choropleth_mapbox(
                population_selected,
                geojson=geojson,
                featureidkey="properties.CTP_KOR_NM",
                locations="행정구역",
                color="인구 수",
                color_continuous_scale="YlOrRd",
                mapbox_style="carto-positron",
                center={"lat": 36.5, "lon": 127.5},
                zoom=6,
                labels={"인구 수": "인구 수"}
            )
            map_fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
            st.plotly_chart(map_fig, use_container_width=True)

        with col2:
            st.subheader("📋 데이터 테이블")
            st.dataframe(population_selected)

        st.markdown("출처: 대한민국 통계청 | 데이터 갱신: 2023년")
    else:
        st.error("선택한 연령대와 성별에 맞는 데이터가 존재하지 않습니다.")

elif menu_option == "🎥 영화 데이터":
    st.subheader("🎥 영화 데이터 화면")
    
    # 영화 데이터 로드
    movie_data = load_movie_data()
    
    # 데이터 테이블 표시
    st.write("### 🎬 영화 관객수 데이터")
    st.dataframe(movie_data, width=1000)  # 넓은 화면에 맞춰 표시
    
    # 시각화: 영화 관객 수 막대 그래프
    st.write("### 🎥 지역별 영화 관객수")
    fig = px.bar(
        movie_data,
        x="지역",
        y="전체_관객수",
        title="지역별 영화 관객수",
        color="전체_관객수",
        labels={"전체_관객수": "전체 관객 수"},
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

elif menu_option == "📚 도서관":
    st.subheader("📚 도서관 데이터 화면")

    # 도서관 데이터 로드
    library_data = load_library_data()

    # 데이터 테이블 표시
    st.write("### 🏫 지역별 도서관 거주 비율")
    st.dataframe(library_data, width=1000)  # 테이블 넓게 표시

    # 시각화: 도서관 거주 비율 막대 그래프
    st.write("### 📊 지역별 도서관 이용 거주 비율")
    fig = px.bar(
        library_data,
        x="지역",
        y="거주비율",
        title="지역별 도서관 이용 거주 비율",
        color="거주비율",
        labels={"거주비율": "거주 비율 (%)"},
        template="plotly_white"
    )
    fig.update_yaxes(range=[80, 100])  # Y축 범위 설정
    st.plotly_chart(fig, use_container_width=True)


