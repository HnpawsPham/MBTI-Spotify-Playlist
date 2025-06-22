import streamlit as st
import validators, spotipy, re
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# SPOTIFY API
auth_manager = SpotifyOAuth(
    client_id = SPOTIFY_CLIENT_ID,
    client_secret = SPOTIFY_CLIENT_SECRET,
    redirect_uri = "https://mbti-spotify-playlist.streamlit.app/callback",
    scope = "playlist-read-private",
    show_dialog=True
)

query_params = st.query_params

if "code" not in query_params:
    login_url = auth_manager.get_authorize_url()
    st.markdown(f"👉 [Nhấn vào đây để đăng nhập Spotify]({login_url})")
    st.stop()

code = query_params["code"]

try:
    token_info = auth_manager.get_access_token(code)
    access_token = token_info["access_token"]
    st.success("Đăng nhập thành công!")
except Exception as e:
    st.error("Lỗi khi lấy access token")
    st.exception(e)
    st.stop()

# create Client
sp = spotipy.Spotify(auth_manager=auth_manager)
st.write(sp.current_user())

# GET PLAYLIST ID BY URL
@st.cache_data
def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

# GET PLAYLIST INFO
def playlist_info(playlist):
    track_ids = [item['track']['id'] for item in playlist['tracks']['items'] if item['track'] and item['track']['id']]
    features = sp.audio_features(track_ids)
    if features:
        features = ([f for f in features if f])  # remove none
    # split into 100 songs for each
    # chunks = [track_ids[i:i+100] for i in range(0, len(track_ids), 100)]
    # print(chunks)
    # all_features = []
    # for chunk in chunks:
    #     try:
    #         features = sp.audio_features(chunk)
    #         if features:
    #             all_features.extend([f for f in features if f])  # remove none 
    #     except Exception as err:
    #         st.warning("Có lỗi xảy ra, vui lòng thử lại!")
    #         print(err)
    #         continue

    # if not all_features:
    #     return None

    # n = len(all_features)
    n = len(features)

    st.write(features)

    return {    
        "danceability": sum(f["danceability"] for f in features) / n,
        "energy": sum(f["energy"] for f in features) / n,
        "tempo": sum(f["tempo"] for f in features) / n,
        "valence": sum(f["valence"] for f in features) / n,
        "acousticness": sum(f["acousticness"] for f in features) / n,
        "instrumentalness": sum(f["instrumentalness"] for f in features) / n
    }


# UI
playlist_url = st.text_input("Dán link playlist Spotify vào đây", placeholder = "https://open.spotify.com/playlist/4SyqPrpD1yGm33Ychi3ac0?si=b3b9d2e173c646ed")

if playlist_url:
    if validators.url(playlist_url):
        playlist_id = extract_playlist_id(playlist_url)
        playlist = sp.playlist(playlist_id, market="VN")
        
        st.write(playlist["name"])
        st.image(playlist["images"][0]["url"], caption="Playlist của bạn")
        
        # show playlist info
        # st.write(playlist_info(playlist))
        st.write(sp.audio_features(['11dFghVXANMlKmJXsNCbNl']))
        
    else:
        st.warning("URL không hợp lệ hoặc không thể tìm thấy")
else:
    st.warning("Bạn cần nhập URL trước khi xem kết quả")