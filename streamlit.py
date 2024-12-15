import streamlit as st

# 제목과 설명
st.title("Streamlit 앱 시작하기")
st.write("안녕하세요! Streamlit 앱에 오신 것을 환영합니다.")

# 간단한 입력과 출력
name = st.text_input("이름을 입력하세요:", "")
if st.button("입력"):
    st.write(f"안녕하세요, {name}님!")
