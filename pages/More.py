import streamlit as st

#RECOMMEND SECTION
st.title("Playlist bạn có thể thích dựa theo kết quả đã dự đoán")

mbti_types = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

if "mbti" not in st.session_state:
    st.session_state.mbti = "ISTJ"

selected_mbti = st.selectbox(
    "Chọn MBTI:", 
    mbti_types,
    index=mbti_types.index(st.session_state.mbti)
)

st.session_state.mbti = selected_mbti