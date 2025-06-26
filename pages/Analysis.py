import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

# CONFIG
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="https://mbti-spotify-playlist.streamlit.app/callback",
    scope="user-read-private",
    cache_path=".cache"  
)

sp = spotipy.Spotify(auth_manager=auth_manager)

def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

def get_features(track_ids):
    results = []
    for track_id in track_ids:
        try:
            features = sp.audio_features([track_id])[0]
            if features:
                results.append(features)
        except spotipy.SpotifyException as e:
            st.warning(f"Skip track {track_id}: {e}")
    return results

# UI
st.header("Phân tích Audio Features của Playlist trên Spotify")

# CHECK LOGIN
if "code" not in st.query_params:
    login_url = auth_manager.get_authorize_url()
    st.markdown(f"Nhấn vào đây để đăng nhập Spotify ({login_url})")
    st.stop()

user = sp.current_user()
st.success(f"Đăng nhập thành công! {user['display_name']} ({user['id']})")

playlist_url = st.text_input("Dán link playlist Spotify:", "")
if playlist_url:
    playlist_id = extract_playlist_id(playlist_url)

    if playlist_id:
        playlist = sp.playlist(playlist_id, market="VN")
        st.write(f"**{playlist['name']}**")
        st.image(playlist["images"][0]["url"], caption="Ảnh Playlist", use_column_width="auto")

        track_ids = [
            item["track"]["id"]
            for item in playlist["tracks"]["items"]
            if item["track"] and item["track"]["id"]
        ]

        features = get_features(track_ids)

        if features:
            avg_values = {
                "danceability": sum(f["danceability"] for f in features) / len(features),
                "energy": sum(f["energy"] for f in features) / len(features),
                "tempo": sum(f["tempo"] for f in features) / len(features),
                "valence": sum(f["valence"] for f in features) / len(features),
                "acousticness": sum(f["acousticness"] for f in features) / len(features),
                "instrumentalness": sum(f["instrumentalness"] for f in features) / len(features),
            }

            st.write("### Avg Audio Features", avg_values)

            if st.checkbox("Xem chi tiết"):
                st.write(features)

        else:
            st.warning("Không có audio features hợp lệ được lấy về.")
    else:
        st.warning("URL playlist không hợp lệ.")
