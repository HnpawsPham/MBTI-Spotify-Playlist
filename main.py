import streamlit as st
from streamlit_option_menu import option_menu
from pages import chatbot, analysis, recommend

# FONT
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Rowdies:wght@300;400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# HIDE DEFAULT NAV
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    div[data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)


# UI
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Rowdies:wght@300;400;700&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    background-color: #121212;
    color: #e0e0e0;
}

h1, h2, h3 {
    font-family: 'Rowdies', sans-serif;
    color: #1DB954;
}

.stButton>button {
    background-color: #1DB954;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    transition: 0.3s ease;
}
.stButton>button:hover {
    background-color: #1ed760;
}

.stChatMessage {
    background-color: #222 !important;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
            
.block-container {
    max-width: 80%;
    margin: 0 auto;
    padding: 2rem;
}

div[role="tab"]:hover {
    background-color: #282828 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# NAV
selected = option_menu(
    menu_title=None,
    options=["Chatbot", "Analysis", "Recommend"],
    icons=["chat", "headphones", "list"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {"padding": "0!important", "background-color": "#191414"},
        "icon": {"color": "white", "font-size": "18px"}, 
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#333",
        },
        "nav-link-selected": {"background-color": "#1DB954", "color": "black"},
    }
)

# LOAD PAGE
if selected == "Chatbot":
    chatbot.run()
elif selected == "Analysis":
    analysis.run()
elif selected == "Recommend":
    recommend.run()