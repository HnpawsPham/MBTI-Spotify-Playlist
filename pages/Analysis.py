import streamlit as st
import validators, spotipy, re, time
from spotipy.oauth2 import SpotifyOAuth
from tensorflow.keras.models import load_model

SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# SPOTIFY API
auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="https://mbti-spotify-playlist1.streamlit.app/callback",
    scope="playlist-read-private user-library-read user-read-email",
    show_dialog=True,
    cache_path=".cache",
    open_browser=False
)

params = st.query_params

if "code" not in params:
    login_url = auth_manager.get_authorize_url()
    st.markdown(f"Nhấn vào đây để đăng nhập Spotify ([link]({login_url}))")
    st.stop()

code = params["code"][0]

try:
    token_info = auth_manager.get_access_token(code, as_dict=False)
    sp = spotipy.Spotify(auth=token_info)
    test_feature = sp.audio_features(["3n3Ppam7vgaVa1iaRUc9Lp"])
    st.write("Test feature:", test_feature)
except Exception as e:
    st.error("Lỗi xác thực hoặc truy cập Spotify API.")
    st.exception(e)
    st.stop()

# GET PLAYLIST ID BY URL
def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

# SAFE AUDIO FEATURE FETCHING

def get_audio_features_safe(track_ids):
    all_features = []
    chunks = [track_ids[i:i + 50] for i in range(0, len(track_ids), 50)]  # Spotify limit: 100, dùng 50 cho an toàn

    for chunk in chunks:
        try:
            features = sp.audio_features(chunk)
            if features:
                all_features.extend([f for f in features if f is not None])
        except Exception as e:
            st.warning(f"Lỗi khi lấy features với chunk: {chunk[:2]}...: {e}")
            continue
        time.sleep(0.1)  
    return all_features

# GET PLAYLIST INFO
def playlist_info(playlist):
    raw_items = playlist["tracks"]["items"]

    track_ids = [item["track"]["id"] for item in raw_items if item["track"] and item["track"].get("id")]

    if not track_ids:
        st.error("Playlist không có track hợp lệ")
        return None

    features = get_audio_features_safe(track_ids)
    if not features:
        st.error("Không thể lấy audio features")
        return None

    n = len(features)
    return {
        "danceability": sum(f["danceability"] for f in features) / n,
        "energy": sum(f["energy"] for f in features) / n,
        "tempo": sum(f["tempo"] for f in features) / n,
        "valence": sum(f["valence"] for f in features) / n,
        "acousticness": sum(f["acousticness"] for f in features) / n,
        "instrumentalness": sum(f["instrumentalness"] for f in features) / n,
    }

# UI
playlist_url = st.text_input("Dán link playlist Spotify vào đây", placeholder="https://open.spotify.com/playlist/...")

if playlist_url:
    if validators.url(playlist_url):
        playlist_id = extract_playlist_id(playlist_url)

        try:
            playlist = sp.playlist(playlist_id)
        except spotipy.SpotifyException as e:
            st.error("Không thể truy cập playlist. Playlist có thể đang để riêng tư.")
            st.exception(e)
            st.stop()

        st.write(f"**{playlist['name']}**")
        if playlist["images"]:
            st.image(playlist["images"][0]["url"], caption="Playlist")

        audio_stats = playlist_info(playlist)
        if audio_stats:
            st.write("**Thống kê audio:**", audio_stats)

    else:
        st.warning("URL không hợp lệ.")
else:
    st.info("Nhập URL để bắt đầu")


def getFuncPairModelPredict():
    model = load_model("./models/func_pair_model.keras")
