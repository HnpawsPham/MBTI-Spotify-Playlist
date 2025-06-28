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
    scope="playlist-read-private user-read-private user-library-read",
    show_dialog=True,
    cache_path=".cache",
    open_browser=False
)

params = st.experimental_get_query_params()

if "code" not in params:
    login_url = auth_manager.get_authorize_url()
    st.markdown(f"Nhấn vào đây để đăng nhập Spotify ({login_url})")
    st.stop()

code = params["code"][0]

try:
    token_info = auth_manager.get_access_token(code)
    access_token = token_info["access_token"]
    sp = spotipy.Spotify(auth=access_token)  # Dùng access token trực tiếp
    st.success("Đăng nhập thành công!")
except Exception as e:
    st.error("Lỗi khi lấy access token")
    st.exception(e)
    st.stop()

# create Client
sp = spotipy.Spotify(auth_manager=auth_manager)

# GET PLAYLIST ID BY URL
def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None


def get_audio_features_safe(track_ids):
    all_features = []
    chunks = [track_ids[i:i + 100] for i in range(0, len(track_ids), 100)]

    for chunk in chunks:
        try:
            features = sp.audio_features(chunk)
            all_features.extend([f for f in features if f is not None])
        except Exception as e:
            st.warning(f"Lỗi với đoạn {chunk[:2]}...: {e}")
        time.sleep(0.2)  
    return all_features


# GET PLAYLIST INFO
def playlist_info(playlist):
    raw_items = playlist['tracks']['items']
    
    track_ids = []
    for item in raw_items:
        if item["track"] and item["track"]["id"]:
            track_ids.append(item["track"]["id"])
        else:
            st.warning(f"Bỏ qua bài không hợp lệ: {item.get('track', {}).get('name', 'Không xác định')}")

    if not track_ids:
        st.error("Không tìm thấy bài nào hợp lệ trong playlist")
        return None

    try:
        features = sp.audio_features(track_ids)
    except spotipy.SpotifyException as e:
        st.error("Lỗi khi gọi `audio_features()`")
        st.exception(e)
        st.write("Track IDs bị lỗi:", track_ids)
        return None

    features = [f for f in features if f is not None]
    if not features:
        st.warning("Không có audio features hợp lệ")
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
playlist_url = st.text_input("Dán link playlist Spotify vào đây", placeholder = "https://open.spotify.com/playlist/4SyqPrpD1yGm33Ychi3ac0?si=b3b9d2e173c646ed")

if playlist_url:
    if validators.url(playlist_url):
        playlist_id = extract_playlist_id(playlist_url)

        try:
            playlist = sp.playlist(playlist_id)  # không truyền market
        except spotipy.SpotifyException as e:
            st.error("Không thể truy cập playlist. Có thể playlist này là riêng tư hoặc không tồn tại.")
            st.exception(e)
            st.stop()
        
        st.write(f"** {playlist['name']}")
        if playlist["images"]:
            st.image(playlist["images"][0]["url"], caption="Ảnh Playlist")

        # Xử lý tiếp
        audio_stats = get_audio_features_safe([
            item["track"]["id"]
            for item in playlist["tracks"]["items"]
            if item["track"] and item["track"]["id"]
        ])
        st.write("audio features:", audio_stats)

    else:
        st.warning("URL không hợp lệ.")
else:
    st.info("Bạn cần nhập URL trước khi xem kết quả")

def getFuncPairModelPredict():
    model = load_model("./models/func_pair_model.keras")
