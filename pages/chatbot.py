import streamlit as st
import json
import pandas as pd
import google.generativeai as genai 
from utilities import *

def run():
    # SETUP
    API = st.secrets["API"]
    genai.configure(api_key = API)

    # READ DATA
    mbti_types = get_16_types()

    # LOAD CONFIG
    with open("config.json", "r", encoding = "utf-8") as f:
        config = json.load(f)

        initial_message = config.get("initial-message")

        bot_name = config.get("bot-name")
        bot_avt = config.get("bot-avt")
        
        user_avt = config.get("user-avt")

    # GENERATE MODEL
    @st.cache_resource
    def load_model():
        return genai.GenerativeModel("gemini-1.5-flash",
                    system_instruction = f"""Bạn tên là ${bot_name}, nhiệm vụ của bạn là tư vấn cho người dùng
                    về loại tính cách của họ và giải đáp các thắc mắc về 16 loại tính cách MBTI.

                    Gồm có 16 loại tính cách ${', '.join(mbti_types)}, bạn cần phân tích những functions như Ni, Ti, Fi, Si,
                    Ne, Te, Fe, Se trong MBTI của người dùng. Hãy trả lời người dùng bằng tiếng Việt sao cho dễ hiểu,
                    kèm theo ví dụ thực tế có liên quan.

                    Bạn cần trả lời tin nhắn mới nhất và sử dụng những tin nhắn trước làm trí nhớ của mình
                    """)

    model = load_model()

    # TITLE
    st.markdown(f'<h1 style="text-align: center;">Talk with HnpawsBot</h1>', unsafe_allow_html=True)

    # RESET CHAT
    cols = st.columns([1, 2, 1])
    with cols[2]:
        if st.button("New chat", key="new_chat", use_container_width=True):
            st.session_state.history = []
            st.session_state.bot_memory = []
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # INITIAL
    if "history" not in st.session_state:
        st.session_state.history = [{
            "role": "assitant",
            "content": initial_message,
            "avt": bot_avt
        }]

    if "bot_memory" not in st.session_state:
        st.session_state.bot_memory = []

    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    # LOAD MESSAGES
    for mess_idx, message in enumerate(st.session_state.history):
        with st.container():
            col = st.columns([7, 1])

            with col[0]:
                with st.chat_message(message["role"], avatar = message["avt"]):
                    st.write(message["content"])

            with col[1]:
                with st.popover("More"):
                    if st.button("Rewind to this message", key = f"rewind {mess_idx}"):
                        st.session_state.history = st.session_state.history[:mess_idx + 1]
                        st.session_state.bot_memory = st.session_state.history[:mess_idx + 1]

                        st.toast("Rewinded!")
                        st.rerun()

                    if st.button("Report this message", key = f"report {mess_idx}"):
                        st.session_state.show_form = True
                        st.session_state.report_idx = mess_idx

    # MAIN CHAT
    if prompt := st.chat_input():
        st.session_state.history.append({
            "role": "user",
            "content": prompt,
            "avt": user_avt
        })

        with st.chat_message("user", avatar=user_avt):
            st.markdown("You")
            st.write(prompt)

        bot_response = model.generate_content(
            f"Tin nhắn trước: {st.session_state.bot_memory}, bạn cần trả lời: {prompt} (người dùng nhắn)"
        ).text

        st.session_state.history.append({
            "role": "assitant",
            "content": bot_response,
            "avt": bot_avt
        })

        with st.chat_message("assitant", avatar=bot_avt):
            st.markdown(bot_name)
            st.write(bot_response)

        st.session_state.bot_memory.append(f"{prompt} (người dùng nhắn)")
        st.session_state.bot_memory.append(f"{bot_response} (bạn nhắn)")
        st.rerun()

    # REPORT FORM
    if st.session_state.show_form:
        idx = st.session_state.report_idx

        if idx:
            st.markdown("### Report")
            st.write(f"Message: {st.session_state.history[idx]["content"]}")
            reason = st.text_input("Your reason: ")

            if st.button("Submit"):
                st.toast("Sended")

                st.session_state.show_form = False
                st.session_state.report_idx = None
                st.rerun()