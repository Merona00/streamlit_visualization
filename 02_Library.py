import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 데이터 로드 함수
@st.cache_data
def load_library_data():
    with open("gdf_korea_sido_2023.json", encoding="utf-8") as f:
        gdf = json.load(f)
    
    library_data = pd.DataFrame({
        "지역": ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
                "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도",
                "경상남도", "제주특별자치도"],
        "거주비율": [96.8, 100, 100, 89.6, 100, 96.1, 100, 100, 85.6, 96.2, 97.3,
                   91.3, 95.7, 89.5, 87.2, 100, 100]
    })
    return gdf, library_data

# 데이터 불러오기
gdf, library_data = load_library_data()

# Streamlit UI 꾸미기
st.set_page_config(page_title="시도별 도서관 이용자 비율", page_icon="📚", layout="wide")
st.title("📚 시도별 도서관 거주 이용자 비율")
st.markdown("""
**전국 시도별 도서관 거주 이용자 비율을 지도 및 산점도 그래프로 시각화합니다.**  
아래 버튼을 눌러 **지도 시각화**와 **막대그래프**를 번갈아 가며 확인할 수 있습니다.
""")

# 버튼 상태 초기화
if "show_map" not in st.session_state:
    st.session_state["show_map"] = True

# 버튼 생성
col1, col2 = st.columns(2)
with col1:
    if st.button("🗺️지도 시각화 보기", use_container_width=True):
        st.session_state["show_map"] = True
with col2:
    if st.button("📊막대그래프 보기", use_container_width=True):
        st.session_state["show_map"] = False


# 지도 시각화
if st.session_state["show_map"]:
    st.subheader("📍 시도별 도서관 거주 이용자 비율 지도")
    fig_map = px.choropleth_mapbox(
        library_data,
        geojson=gdf,
        featureidkey="properties.CTP_KOR_NM",
        locations="지역",
        color="거주비율",
        color_continuous_scale="Blues",
        mapbox_style="carto-positron",
        center={"lat": 36.5, "lon": 127.5},
        zoom=5,
    )
    st.plotly_chart(fig_map, use_container_width=True)
# 산점도 그래프
else:
    st.subheader("📊 시도별 도서관 거주 이용자 비율 막대그래프")
    fig_bar = px.bar(
        library_data,
        x="지역",
        y="거주비율",
        color="거주비율",
        color_continuous_scale="Blues",
        title="시도별 도서관 거주 이용자 비율 막대그래프",
        labels={"거주비율": "거주비율 (%)", "지역": "지역"}
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
