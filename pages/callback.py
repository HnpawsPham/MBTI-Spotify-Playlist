import streamlit as st

query_params = st.query_params

if "code" in query_params:
    code = query_params["code"]
    st.write("Đang chuyển hướng...")
    st.markdown(f"""
        <meta http-equiv="refresh" content="0; url=/Analysis?code={code}" />
    """, unsafe_allow_html=True)
else:
    st.error("Không tìm thấy mã xác thực")
