import streamlit as st
import validators, spotipy, re, time
from spotipy.oauth2 import SpotifyOAuth
from tensorflow.keras.models import load_model

SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# SPOTIFY API
if 'spotify' not in st.session_state:
    if st.button("Login with Spotify"):
        sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri="https://mbti-spotify-playlist1.streamlit.app/callback",
            scope="user-library-read playlist-read-private",
            open_browser=False 
        )
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"Login: ({auth_url})", unsafe_allow_html=True)

    if st.experimental_get_query_params().get("code"):
        code = st.experimental_get_query_params()["code"][0]
        try:
           token_info = sp_oauth.get_access_token(code)
           st.session_state.spotify = spotipy.Spotify(auth=token_info['access_token'])
           st.success("Authentication successful!")
        except Exception as e:
           st.error(f"Authentication failed: {e}")

if 'spotify' in st.session_state:
    st.write("You are now logged in!")

    results = st.session_state.spotify.current_user_playlists()
    for item in results['items']:
        st.write(item['name'])

# GET PLAYLIST ID BY URL
def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

# SAFE AUDIO FEATURE FETCHING
def get_audio_features(track_ids):
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

    features = get_audio_features(track_ids)
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
            st.error("Không thể truy cập playlist. Playlist có thể đang để riêng tư")
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


# USE TRAINED MODELS FOR GIVING PREDICTIONS
def getFuncPairModelPredict():
    model = load_model("./models/func_pair_model.keras")
