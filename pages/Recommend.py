import streamlit as st
import pandas as pd
import time
from utilities import *
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# SELECTBOX
st.title("Playlist bạn có thể thích dựa theo kết quả đã dự đoán")

mbti_types = get_16_types()

if "mbti" not in st.session_state:
    st.session_state.mbti = "ISTJ"

selected_mbti = st.selectbox(
    "Chọn MBTI:", 
    mbti_types,
    index=mbti_types.index(st.session_state.mbti)
)

st.session_state.mbti = selected_mbti

# RECOMMEND SECTION
df = pd.read_csv(f"./csv/{selected_mbti}_df.csv")

playlist_container = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Rowdies:wght@300;400;700&display=swap" rel="stylesheet">

<style>
    /* Scrollbar Custom */
    .container::-webkit-scrollbar {
        height: 5px;
    }
    .container::-webkit-scrollbar-track {
        background: #eee;
        border-radius: 10px;
    }
    .container::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 10px;
    }
    .container::-webkit-scrollbar-thumb:hover {
        background: #999;
    }

    .container{
        display: flex;
        gap: 20px;
        overflow-x: scroll;
        padding: 10px;
        background-color: #A31D1D;
        border-radius: 15px;
    }
    .card{
        height: 90%;
        max-width: 325px;
        min-width: 325px;
        flex: 0 0 auto;
    }
    .card h3{
        padding: 10px 0 15px 0;
        margin: 0;
        color: #E5D0AC;
        font-family: "Rowdies", sans-serif;
        text-align: center;
        height: 10%;
    }
</style>

<div class="container">
"""

for i, row in df.head(15).iterrows():
    playlist_id = row["playlist_id"]
    playlist_name = shorten_name(row["playlist_name"])

    playlist_card = f"""
    <div class="card">
        <h3>{playlist_name}</h3>
        <iframe style="border-radius:12px"
            src="https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator"
            width="100%" height="152" frameBorder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy">
        </iframe>
    </div>
    """
    playlist_container += playlist_card
    time.sleep(0.2)

playlist_container += "</div>"
st.components.v1.html(playlist_container, height=300)

# CHARTS
# radar chart
st.markdown(f'<h1 style="text-align: center;">RADAR CHART (All playlist)</h1>', unsafe_allow_html=True)

chart_df = df[keep_col]

scaler = MinMaxScaler()
chart_df = pd.DataFrame(
    scaler.fit_transform(df[keep_col]),
    columns=keep_col
)

mean = chart_df.mean()
values = mean.values
labels = mean.index

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r = values,
    theta= labels,
    fill="toself",
    name=selected_mbti,
    line=dict(color="green")
))

fig.update_layout(
    polar=dict(
        radialaxis = dict(visible=True, range=[0, max(values) * 1.2])
    ))

st.plotly_chart(fig, use_container_width=True)

# bar chart
st.markdown(f'<h1 style="text-align: center;">BAR CHART (All playlist)</h1>', unsafe_allow_html=True)

bar_fig = px.bar(
    x = values,
    y = labels,
    labels={'x': "Trung bình",
            'y': 'Đặc trưng'},
    color_continuous_scale='YlOrRd' 
)

bar_fig.update_layout(yaxis={"categoryorder": "total ascending"})

st.plotly_chart(bar_fig, use_container_width=True)